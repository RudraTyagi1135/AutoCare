# ============================ #
#   Heart Model Data Transformation
# ============================ #

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from typing import List, Dict

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
    Heart model data transformation:
    Final features (order):
    age_category, gender, obesity, hypertension, highchol,
    heart_attack_history, chest_pain, smoking, alcohol, physactivity, stress_category

    Target: 'heart_disease'
    """

    TARGET_COLUMN = "heart_disease"
    FINAL_FEATURES = [
        "age_category",
        "gender",
        "obesity",
        "hypertension",
        "highchol",
        "heart_attack_history",
        "chest_pain",
        "smoking",
        "alcohol",
        "physactivity",
        "stress_category",
    ]

    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact

            self.age_mapping: Dict[str, int] = {
                '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
                '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
                '70-74': 11, '75-79': 12, '80 or older': 13
            }

            logging.info("✅ Heart DataTransformation instance created successfully.")
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
        if "age_category" in df.columns and df["age_category"].dtype == object:
            df["age_category"] = df["age_category"].map(lambda x: self.age_mapping.get(str(x).strip(), np.nan))
        elif "age" in df.columns:
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

    def _ensure_obesity(self, df: pd.DataFrame) -> pd.DataFrame:
        # If obesity present, ensure 0/1; else compute from bmi if available
        if "obesity" in df.columns:
            df["obesity"] = df["obesity"].apply(lambda x: 1 if str(x).strip().lower() in ["1", "1.0", "yes", "y", "true"] else 0)
            return df

        if "bmi" in df.columns:
            df["obesity"] = df["bmi"].apply(lambda x: 1 if float(x) > 29 else 0)
            logging.info("Computed 'obesity' from 'bmi'.")
            return df

        raise AutoCareException("Heart dataset must contain 'obesity' (0/1) or 'bmi' to compute it.", sys)

    def _compute_hypertension_if_needed(self, df: pd.DataFrame) -> pd.DataFrame:
        if "hypertension" not in df.columns and {"systolic", "diastolic"}.issubset(df.columns):
            df["hypertension"] = df.apply(
                lambda r: 1 if (float(r.get("systolic", 0)) >= 130 or float(r.get("diastolic", 0)) >= 85) else 0,
                axis=1
            )
            logging.info("Computed 'hypertension' from systolic/diastolic.")
        return df

    def _map_yes_no(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        if column in df.columns:
            df[column] = df[column].apply(lambda x: 1 if str(x).strip().lower() in ["1", "yes", "y", "true"] else 0)
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

            # Ensure obesity exists
            df = self._ensure_obesity(df)

            # Hypertension required
            df = self._compute_hypertension_if_needed(df)

            # Mappings
            df = self._map_gender(df)
            df = self._map_age(df)

            # Map yes/no style columns
            df = self._map_yes_no(df, "heart_attack_history")  # normalized name expected
            # also accept older name 'prior_heart_attack'
            if "prior_heart_attack" in df.columns and "heart_attack_history" not in df.columns:
                df["heart_attack_history"] = df["prior_heart_attack"].apply(lambda x: 1 if str(x).strip().lower() in ["1", "yes", "y", "true"] else 0)

            df = self._map_yes_no(df, "chest_pain")
            df = self._map_yes_no(df, "smoking")
            df = self._map_yes_no(df, "alcohol")
            df = self._map_yes_no(df, "physactivity")
            df = self._map_yes_no(df, "highchol")
            df = self._map_stress(df)

            # Drop helpers not used for training
            drop_cols = ["Unnamed: 0", "height", "weight", "bmi", "systolic", "diastolic", "prior_heart_attack"]
            df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

            # Ensure target column present
            if self.TARGET_COLUMN in df.columns:
                df[self.TARGET_COLUMN] = df[self.TARGET_COLUMN].astype(int)
            else:
                raise AutoCareException(f"Target column '{self.TARGET_COLUMN}' not found in heart dataset.", sys)

            logging.info(f"Processed DF Columns: {list(df.columns)}")
            return df
        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Main
    # -----------------------------
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("🚀 Starting HEART data transformation...")

            train_df = self._load_csv(self.data_validation_artifact.valid_train_file_path)
            test_df = self._load_csv(self.data_validation_artifact.valid_test_file_path)

            train_df = self._prepare_dataframe(train_df)
            test_df = self._prepare_dataframe(test_df)

            # Ensure all required features exist
            missing = [f for f in self.FINAL_FEATURES if f not in train_df.columns]
            if missing:
                raise AutoCareException(f"Missing required heart feature(s) in train set: {missing}", sys)

            feature_cols: List[str] = self.FINAL_FEATURES.copy()

            # Sanity between train/test
            missing_in_test = set(feature_cols) - set(test_df.columns)
            if missing_in_test:
                raise AutoCareException(f"Feature columns missing in test set: {missing_in_test}", sys)

            X_train = train_df[feature_cols].values
            y_train = train_df[self.TARGET_COLUMN].values
            X_test = test_df[feature_cols].values
            y_test = test_df[self.TARGET_COLUMN].values

            imputer = SimpleImputer(strategy="median")
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            preprocessor = {"imputer": imputer, "scaler": scaler, "feature_columns": feature_cols}
            os.makedirs(os.path.dirname(self.config.transformed_object_file_path), exist_ok=True)
            save_object(self.config.transformed_object_file_path, preprocessor)
            logging.info(f"Preprocessor saved at: {self.config.transformed_object_file_path}")

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

            logging.info("✅ HEART Data Transformation Completed!")
            return artifact

        except Exception as e:
            raise AutoCareException(e, sys)
