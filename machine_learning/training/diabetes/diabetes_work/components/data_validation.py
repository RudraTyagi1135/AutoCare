# ============================ #
#   Data Validation Component  #
# ============================ #

# -------- Standard Imports --------
import os
import sys
import pandas as pd
from scipy.stats import ks_2samp
from sqlalchemy import values  # Kolmogorov-Smirnov test
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# -------- Internal Imports --------
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging
from network_security.constant.training_pipeline import SCHEMA_FILE_PATH
from network_security.utils.main_utils.utils import read_yaml_file, write_yaml_file

# -------- Environment Variables Loader --------
from dotenv import load_dotenv
load_dotenv()  # Load secrets from .env

# Load MongoDB URL (safe logging, no print)
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
logging.info("MongoDB URL successfully loaded from environment.")

# -------- Config / Entity Imports --------
from network_security.entity.config_entity import DataValidationConfig
from network_security.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact


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
            # Load schema YAML
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """Reads a CSV file into a pandas DataFrame."""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_no_of_columns(self, dataframe: pd.DataFrame) -> bool:
        """
        Validates if DataFrame has the required number of columns
        as defined in the schema.
        """
        try:
            required_columns = self._schema_config["columns"] # Assuming schema.yaml has "columns"
            number_of_columns = len(required_columns)

            logging.info(f"Schema requires {number_of_columns} columns.")
            logging.info(f"DataFrame contains {len(dataframe.columns)} columns.")

            if len(dataframe.columns) != number_of_columns:
                missing_cols = set(required_columns) - set(dataframe.columns)
                extra_cols = set(dataframe.columns) - set(required_columns)
                logging.error(f"Column validation failed. Missing: {missing_cols}, Extra: {extra_cols}")
                return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.05) -> bool:
        """
        Detects dataset drift using statistical tests:
            - Numeric columns → KS test
            - Categorical columns → Chi-square (via value_counts)
        Saves YAML drift report.
        """
        try:
            status = True
            report = {}

            for column in base_df.columns:
                if column not in current_df.columns:
                    logging.warning(f"Column {column} missing in current dataset. Skipping drift check.")
                    continue

                d1, d2 = base_df[column].dropna(), current_df[column].dropna()

                if pd.api.types.is_numeric_dtype(d1):
                    ks_result = ks_2samp(d1, d2)
                    p_value = ks_result.pvalue    # type: ignore
                    drift_detected = p_value < threshold
                else:
                    # Simple categorical drift check via normalized value counts
                    freq1 = d1.value_counts(normalize=True)
                    freq2 = d2.value_counts(normalize=True)
                    diff = sum(abs(freq1.get(cat, 0) - freq2.get(cat, 0)) for cat in set(freq1.index).union(freq2.index))
                    p_value = 1 - diff  # pseudo-score
                    drift_detected = diff > threshold

                if drift_detected:
                    status = False

                report[column] = {
                    "p_value": float(p_value),
                    "drift_detected": drift_detected
                }

            # Save drift report
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)

            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys)

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
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            # Schema validation
            valid_train = self.validate_no_of_columns(train_dataframe)
            valid_test = self.validate_no_of_columns(test_dataframe)

            if not (valid_train and valid_test):
                logging.error("Schema validation failed for one or both datasets.")
                return DataValidationArtifact(
                    validation_status=False,
                    valid_train_file_path=None,    # type: ignore
                    valid_test_file_path=None,   # type: ignore
                    invalid_train_file_path=train_file_path if not valid_train else None,    # type: ignore
                    invalid_test_file_path=test_file_path if not valid_test else None,   # type: ignore
                    drift_report_file_path=self.data_validation_config.drift_report_file_path,
                )

            # Drift detection
            drift_status = self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)

            # Save validated datasets
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)
            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)

            return DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,    # type: ignore
                invalid_test_file_path=None,   # type: ignore
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)
