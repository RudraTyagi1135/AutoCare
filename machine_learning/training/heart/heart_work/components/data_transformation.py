# ============================ #
#   Data Transformation Component
# ============================ #

# -------- Standard Imports --------
import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# -------- Internal Imports --------
from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging
from machine_learning.training.heart.heart_work.entity.config_entity import DataTransformationConfig
from machine_learning.training.heart.heart_work.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact,
)
from machine_learning.ml_utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    """
    Performs transformation of validated diabetes datasets:
    - Reads validated train/test CSVs
    - Applies preprocessing (mapping, encoding, scaling)
    - Saves transformed numpy arrays and preprocessor object
    """

    TARGET_COLUMN = "heart"

    # Columns that represent boolean-like categories
    BOOLEAN_COLUMNS = ["alcohol", "smoking", "physactivity", "diffwalk", "highchol"]

    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact

            # Age group mapping you defined
            self.age_mapping = {
                '0-17': 0, '18-24': 1, '25-29': 2, '30-34': 3, '35-39': 4,
                '40-44': 5, '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9,
                '65-69': 10, '70-74': 11, '75-79': 12, '80 or older': 13
            }

            logging.info("✅ DataTransformation instance created successfully.")

        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Helper: Read CSV
    # -----------------------------
    def _load_csv(self, path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(path)
            logging.info(f"Loaded dataset: {path}, Shape: {df.shape}")
            return df
        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Helper: Map Gender
    # -----------------------------
    def _map_gender(self, df: pd.DataFrame) -> pd.DataFrame:
        if "gender" in df.columns:
            df["gender"] = df["gender"].map(lambda x: 1 if str(x).strip().lower() in ["male", "m"] else 0)
        return df

    # -----------------------------
    # Helper: Map Age Category
    # -----------------------------
    def _map_age_category(self, df: pd.DataFrame) -> pd.DataFrame:
        if "age_category" in df.columns and df["age_category"].dtype == object:
            df["age_category"] = df["age_category"].map(self.age_mapping)
        return df

    # -----------------------------
    # Helper: Map Boolean-like Columns
    # -----------------------------
    def _map_boolean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.BOOLEAN_COLUMNS:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: 1 if str(x).strip().lower() in ["1", "yes", "y", "true", "t"] else 0)
        return df

    # -----------------------------
    # Helper: Map Stress Category
    # -----------------------------
    def _map_stress(self, df: pd.DataFrame) -> pd.DataFrame:
        if "stress_category" in df.columns:
            mapping = {
                "no stress": 0, "mild": 1, "moderate": 2, "high": 3, "severe": 4
            }
            if df["stress_category"].dtype == object:
                df["stress_category"] = df["stress_category"].map(
                    lambda x: mapping.get(str(x).strip().lower(), np.nan)
                )
        return df

    # -----------------------------
    # Helper: Compute BMI (if missing)
    # -----------------------------
    def _compute_bmi_if_needed(self, df: pd.DataFrame) -> pd.DataFrame:
        if "bmi" not in df.columns and all(col in df.columns for col in ["height", "weight"]):
            df["bmi"] = df["weight"] / ((df["height"] / 100) ** 2)
        return df

    # -----------------------------
    # Helper: Compute Hypertension (if needed)
    # -----------------------------
    def _compute_hypertension_if_needed(self, df: pd.DataFrame) -> pd.DataFrame:
        if all(col in df.columns for col in ["systolic", "diastolic"]) and "hypertension" not in df.columns:
            df["hypertension"] = df.apply(
                lambda r: 1 if (float(r.get("systolic", 0)) >= 130 or float(r.get("diastolic", 0)) >= 85) else 0,
                axis=1,
            )
        return df

    # -----------------------------
    # Helper: Clean + Prepare DataFrame
    # -----------------------------
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()

            # Apply all transformations
            df = self._compute_bmi_if_needed(df)
            df = self._compute_hypertension_if_needed(df)
            df = self._map_gender(df)
            df = self._map_age_category(df)
            df = self._map_boolean_columns(df)
            df = self._map_stress(df)

            # Drop unwanted index columns if exist
            if "Unnamed: 0" in df.columns:
                df.drop(columns=["Unnamed: 0"], inplace=True)

            # Ensure target is integer
            if self.TARGET_COLUMN in df.columns:
                df[self.TARGET_COLUMN] = df[self.TARGET_COLUMN].astype(int)

            logging.info(f"DataFrame processed. Final columns: {list(df.columns)}")
            return df

        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Main Transformation Function
    # -----------------------------
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("🚀 Initiating data transformation...")

            # Step 1: Load validated datasets
            train_path = self.data_validation_artifact.valid_train_file_path
            test_path = self.data_validation_artifact.valid_test_file_path
            train_df = self._load_csv(train_path)
            test_df = self._load_csv(test_path)

            # Step 2: Clean and preprocess dataframes
            train_df = self._prepare_dataframe(train_df)
            test_df = self._prepare_dataframe(test_df)

            # Step 3: Separate features and target
            if self.TARGET_COLUMN not in train_df.columns:
                raise Exception(f"Target column '{self.TARGET_COLUMN}' not found in dataset!")

            feature_cols = [col for col in train_df.columns if col != self.TARGET_COLUMN]
            X_train, y_train = train_df[feature_cols].values, train_df[self.TARGET_COLUMN].values
            X_test, y_test = test_df[feature_cols].values, test_df[self.TARGET_COLUMN].values

            # Step 4: Handle missing values and scale
            imputer = SimpleImputer(strategy="median")
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Step 5: Save preprocessor (imputer + scaler + feature info)
            preprocessor = {
                "imputer": imputer,
                "scaler": scaler,
                "feature_columns": feature_cols
            }

            save_object(self.config.transformed_object_file_path, preprocessor)
            logging.info(f"Preprocessor object saved at: {self.config.transformed_object_file_path}")

            # Step 6: Combine features and target
            train_arr = np.hstack([X_train_scaled, y_train.reshape(-1, 1)])
            test_arr = np.hstack([X_test_scaled, y_test.reshape(-1, 1)])

            # Step 7: Save transformed arrays
            save_numpy_array_data(self.config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.config.transformed_test_file_path, test_arr)
            logging.info("Transformed train/test arrays saved successfully.")

            # Step 8: Create and return artifact
            transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.config.transformed_object_file_path,
                transformed_train_file_path=self.config.transformed_train_file_path,
                transformed_test_file_path=self.config.transformed_test_file_path,
            )

            logging.info("✅ Data Transformation completed successfully.")
            return transformation_artifact

        except Exception as e:
            raise AutoCareException(e, sys)