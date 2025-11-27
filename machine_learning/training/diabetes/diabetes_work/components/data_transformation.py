# ============================ #
#  Diabetes Data Transformation
# ============================ #

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging
from machine_learning.training.diabetes.diabetes_work.entity.config_entity import DataTransformationConfig
from machine_learning.training.diabetes.diabetes_work.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)
from machine_learning.ml_utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    """
    Diabetes data transformation:
    - Final feature order: age_category, gender, bmi, hypertension,
      smoking, alcohol, highchol, diffwalk, stress_category, physactivity
    - Target: 'diabetes'
    - Compute BMI if height & weight present.
    - Compute hypertension if systolic/diastolic present.
    - Map gender, booleans, stress.
    - Impute (median) and scale, save preprocessor and arrays.
    """

    TARGET_COLUMN = "diabetes"
    FINAL_FEATURES = [
        "age_category",
        "gender",
        "bmi",
        "hypertension",
        "smoking",
        "alcohol",
        "highchol",
        "diffwalk",
        "stress_category",
        "physactivity",
    ]

    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact

            # Age bucketing mapping consistent with plan
            self.age_mapping = {
                '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
                '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
                '70-74': 11, '75-79': 12, '80 or older': 13
            }

            logging.info("✅ Diabetes DataTransformation instance created successfully.")
        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Helpers
    # -----------------------------
    def _load_csv(self, path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(path)
            logging.info(f"Loaded dataset: {path}, Shape: {df.shape}")
            return df
        except Exception as e:
            raise AutoCareException(e, sys)

    def _map_gender(self, df: pd.DataFrame) -> pd.DataFrame:
        if "gender" in df.columns:
            df["gender"] = df["gender"].map(lambda x: 1 if str(x).strip().lower() in ["male", "m"] else 0)
        return df

    def _map_age(self, df: pd.DataFrame) -> pd.DataFrame:
        # Accept existing encoded age_category or text bucket, or numeric age
        if "age_category" in df.columns and df["age_category"].dtype == object:
            df["age_category"] = df["age_category"].map(lambda x: self.age_mapping.get(str(x).strip(), np.nan))
        elif "age" in df.columns:
            # numeric age -> bucket
            def age_to_bucket(a):
                try:
                    a = float(a)
                except Exception:
                    return np.nan
                if a <= 24: return 1
                if 25 <= a <= 29: return 2
                if 30 <= a <= 34: return 3
                if 35 <= a <= 39: return 4
                if 40 <= a <= 44: return 5
                if 45 <= a <= 49: return 6
                if 50 <= a <= 54: return 7
                if 55 <= a <= 59: return 8
                if 60 <= a <= 64: return 9
                if 65 <= a <= 69: return 10
                if 70 <= a <= 74: return 11
                if 75 <= a <= 79: return 12
                return 13
            df["age_category"] = df["age"].apply(age_to_bucket)
        return df

    def _compute_bmi_if_needed(self, df: pd.DataFrame) -> pd.DataFrame:
        # If BMI missing but height & weight present, compute.
        if "bmi" not in df.columns and {"height", "weight"}.issubset(df.columns):
            df["bmi"] = df["weight"] / ((df["height"] / 100) ** 2)
            logging.info("Computed 'bmi' from height & weight.")
        return df

    def _compute_hypertension_if_needed(self, df: pd.DataFrame) -> pd.DataFrame:
        # If hypertension missing but systolic/diastolic present, compute.
        if "hypertension" not in df.columns and {"systolic", "diastolic"}.issubset(df.columns):
            df["hypertension"] = df.apply(
                lambda r: 1 if (float(r.get("systolic", 0)) >= 130 or float(r.get("diastolic", 0)) >= 85) else 0,
                axis=1
            )
            logging.info("Computed 'hypertension' from systolic/diastolic.")
        return df

    def _map_boolean(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: 1 if str(x).strip().lower() in ["1", "yes", "y", "true", "t"] else 0)
        return df

    def _map_stress(self, df: pd.DataFrame) -> pd.DataFrame:
        if "stress_category" in df.columns:
            mapping = {"no stress": 0, "mild": 1, "moderate": 2, "high": 3, "severe": 4}
            if df["stress_category"].dtype == object:
                df["stress_category"] = df["stress_category"].map(lambda x: mapping.get(str(x).strip().lower(), np.nan))
        return df

    # -----------------------------
    # Prepare DF
    # -----------------------------
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()

            # Compute/Map core fields
            df = self._compute_bmi_if_needed(df)
            df = self._compute_hypertension_if_needed(df)
            df = self._map_gender(df)
            df = self._map_age(df)

            # Boolean mappings for required boolean columns
            for col in ["smoking", "alcohol", "physactivity", "diffwalk", "highchol"]:
                df = self._map_boolean(df, col)

            df = self._map_stress(df)

            # Drop helper/unwanted columns if present
            drop_cols = ["Unnamed: 0", "height", "weight", "systolic", "diastolic"]
            df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

            # Ensure target type
            if self.TARGET_COLUMN in df.columns:
                df[self.TARGET_COLUMN] = df[self.TARGET_COLUMN].astype(int)

            logging.info(f"Processed DF Columns: {list(df.columns)}")
            return df
        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Main
    # -----------------------------
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("🚀 Initiating diabetes data transformation...")

            # Load validated CSVs
            train_df = self._load_csv(self.data_validation_artifact.valid_train_file_path)
            test_df = self._load_csv(self.data_validation_artifact.valid_test_file_path)

            # Prepare
            train_df = self._prepare_dataframe(train_df)
            test_df = self._prepare_dataframe(test_df)

            # Ensure target present
            if self.TARGET_COLUMN not in train_df.columns:
                raise AutoCareException(f"Target column '{self.TARGET_COLUMN}' not found in diabetes dataset.", sys)

            # Build features list strictly in FINAL_FEATURES order but include only present ones (error if missing)
            missing = [f for f in self.FINAL_FEATURES if f not in train_df.columns]
            if missing:
                raise AutoCareException(f"Missing required diabetes feature(s) in train set: {missing}", sys)

            feature_cols = self.FINAL_FEATURES.copy()

            # Separate arrays
            X_train = train_df[feature_cols].values
            y_train = train_df[self.TARGET_COLUMN].values
            X_test = test_df[feature_cols].values
            y_test = test_df[self.TARGET_COLUMN].values

            # Impute & scale
            imputer = SimpleImputer(strategy="median")
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Save preprocessor (imputer+scaler+feature_columns)
            preprocessor = {
                "imputer": imputer,
                "scaler": scaler,
                "feature_columns": feature_cols
            }
            os.makedirs(os.path.dirname(self.config.transformed_object_file_path), exist_ok=True)
            save_object(self.config.transformed_object_file_path, preprocessor)
            logging.info(f"Preprocessor object saved at: {self.config.transformed_object_file_path}")

            # Combine features + target and save arrays
            train_arr = np.c_[X_train_scaled, y_train]
            test_arr = np.c_[X_test_scaled, y_test]

            os.makedirs(os.path.dirname(self.config.transformed_train_file_path), exist_ok=True)
            save_numpy_array_data(self.config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.config.transformed_test_file_path, test_arr)
            logging.info("Transformed train/test arrays saved successfully.")

            artifact = DataTransformationArtifact(
                transformed_object_file_path=self.config.transformed_object_file_path,
                transformed_train_file_path=self.config.transformed_train_file_path,
                transformed_test_file_path=self.config.transformed_test_file_path,
            )

            logging.info("✅ Diabetes Data Transformation completed successfully.")
            return artifact

        except Exception as e:
            raise AutoCareException(e, sys)
