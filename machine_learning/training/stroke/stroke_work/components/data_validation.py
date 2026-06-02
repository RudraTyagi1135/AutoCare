# ============================ #
#   Data Validation Component  #
# ============================ #

# -------- Standard Imports --------
import os
import sys
import pandas as pd
from scipy.stats import ks_2samp
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# -------- Internal Imports --------
from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging
from machine_learning.ml_utils.main_utils.utils import read_yaml_file, write_yaml_file

# -------- Config / Entity Imports --------
from machine_learning.training.stroke.stroke_work.entity.config_entity import DataValidationConfig
from machine_learning.training.stroke.stroke_work.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact
)

# -------- Schema Path --------
SCHEMA_FILE_PATH = os.path.join(
    "machine_learning", "training", "stroke", "stroke_work", "schema", "stroke_schema.yaml"
)


class DataValidation:
    """
    Component for validating ingested datasets:
        - Schema-driven column validation
        - Dataset drift detection (numeric & categorical)
        - Drift report generation (YAML)
        - Returns DataValidationArtifact
    """

    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config

            # Load schema YAML (must exist)
            if not os.path.exists(SCHEMA_FILE_PATH):
                raise FileNotFoundError(f"Schema file not found at: {SCHEMA_FILE_PATH}")

            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            logging.info(f"Schema file loaded successfully from {SCHEMA_FILE_PATH}")

        except Exception as e:
            raise AutoCareException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """Reads a CSV file into a pandas DataFrame."""
        try:
            logging.info(f"Reading dataset from: {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            raise AutoCareException(e, sys)

    def validate_no_of_columns(self, dataframe: pd.DataFrame) -> bool:
        """
        Validates if DataFrame has the required number of columns
        as defined in the diabetes schema.
        """
        try:
            required_columns = list(self._schema_config["columns"].keys())
            number_of_columns = len(required_columns)

            logging.info(f"Schema requires {number_of_columns} columns.")
            logging.info(f"DataFrame contains {len(dataframe.columns)} columns.")

            if len(dataframe.columns) != number_of_columns:
                missing_cols = set(required_columns) - set(dataframe.columns)
                extra_cols = set(dataframe.columns) - set(required_columns)
                logging.error(f"❌ Column validation failed.")
                logging.error(f"Missing Columns: {missing_cols}")
                logging.error(f"Extra Columns: {extra_cols}")
                return False

            logging.info("✅ Column validation successful.")
            return True

        except Exception as e:
            raise AutoCareException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.05) -> bool:
        """
        Detects dataset drift using statistical tests:
            - Numeric columns → KS test
            - Categorical columns → frequency distribution difference
        Saves YAML drift report.
        """
        try:
            logging.info("Starting dataset drift detection...")
            status = True
            drift_report = {}

            for column in base_df.columns:
                if column not in current_df.columns:
                    logging.warning(f"⚠ Column {column} missing in test dataset. Skipping drift check.")
                    continue

                d1, d2 = base_df[column].dropna(), current_df[column].dropna()

                if pd.api.types.is_numeric_dtype(d1):
                    ks_result = ks_2samp(d1, d2)
                    p_value = ks_result.pvalue
                    drift_detected = p_value < threshold
                else:
                    freq1 = d1.value_counts(normalize=True)
                    freq2 = d2.value_counts(normalize=True)
                    diff = sum(abs(freq1.get(cat, 0) - freq2.get(cat, 0)) for cat in set(freq1.index).union(freq2.index))
                    p_value = 1 - diff
                    drift_detected = diff > threshold

                drift_report[column] = {
                    "p_value": float(p_value),
                    "drift_detected": drift_detected
                }

                if drift_detected:
                    status = False
                    logging.warning(f"⚠ Drift detected in column: {column}")

            # Save drift report
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=drift_report)

            logging.info(f"✅ Drift report saved at: {drift_report_file_path}")
            return status

        except Exception as e:
            raise AutoCareException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Executes data validation:
            1. Reads ingested train/test datasets
            2. Validates schema compliance
            3. Detects dataset drift
            4. Saves valid datasets & drift report
            5. Returns DataValidationArtifact
        """
        try:
            logging.info("🚀 Initiating Data Validation Process...")

            # Step 1: Read train/test data
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            train_df = self.read_data(train_file_path)
            test_df = self.read_data(test_file_path)

            # Step 2: Schema validation
            valid_train = self.validate_no_of_columns(train_df)
            valid_test = self.validate_no_of_columns(test_df)

            if not (valid_train and valid_test):
                logging.info("❌ Schema validation failed for one or both datasets.")
                return DataValidationArtifact(
                    validation_status=False,
                    valid_train_file_path=None,
                    valid_test_file_path=None,
                    invalid_train_file_path=train_file_path if not valid_train else None,
                    invalid_test_file_path=test_file_path if not valid_test else None,
                    drift_report_file_path=self.data_validation_config.drift_report_file_path,
                )

            # Step 3: Drift detection
            drift_status = self.detect_dataset_drift(base_df=train_df, current_df=test_df)

            # Step 4: Save validated datasets
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)
            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)
            logging.info("✅ Validated datasets saved successfully.")

            # Step 5: Return artifact
            data_validation_artifact = DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )

            logging.info(f"🎯 Data Validation Completed | Drift Status: {drift_status}")
            return data_validation_artifact

        except Exception as e:
            raise AutoCareException(e, sys)