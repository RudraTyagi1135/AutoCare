# =============================================== #
#               Stroke Data Transformation
# =============================================== #

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging
from machine_learning.training.stroke.stroke_work.entity.config_entity import DataTransformationConfig
from machine_learning.training.stroke.stroke_work.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact,
)
from machine_learning.ml_utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    """
    Stroke DataTransformation:
    Final features (order expected):
    age_category, gender, bmi, smoking, alcohol, physactivity, sleeptime, stress_category, diffwalk
    Target: 'stroke'
    """

    TARGET_COLUMN = "stroke"
    FINAL_FEATURES = [
        "age_category",
        "gender",
        "bmi",
        "smoking",
        "alcohol",
        "physactivity",
        "sleeptime",
        "stress_category",
        "diffwalk",
    ]

    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact

            self.age_mapping = {
                '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
                '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
                '70-74': 11, '75-79': 12, '80 or older': 13
            }

            logging.info("✅ Stroke DataTransformation instance created successfully.")
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

    def _compute_bmi_if_needed(self, df: pd.DataFrame) -> pd.DataFrame:
        if "bmi" not in df.columns and {"height", "weight"}.issubset(df.columns):
            df["bmi"] = df["weight"] / ((df["height"] / 100) ** 2)
            logging.info("Computed 'bmi' from height & weight.")
        return df

    def _map_boolean(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: 1 if str(x).strip().lower() in ["1", "yes", "y", "true"] else 0)
        return df

    def _map_stress(self, df: pd.DataFrame) -> pd.DataFrame:
        if "stress_category" in df.columns:
            mapping = {"no stress": 0, "mild": 1, "moderate": 2, "high": 3, "severe": 4}
            if df["stress_category"].dtype == object:
                df["stress_category"] = df["stress_category"].map(lambda x: mapping.get(str(x).strip().lower(), np.nan))
        return df

    def _normalize_sleep_field(self, df: pd.DataFrame) -> pd.DataFrame:
        # Accept 'sleeptime' or 'sleep_time' or 'sleep_hours' from various sources and normalize to 'sleeptime'
        for candidate in ["sleeptime", "sleep_time", "sleep_hours", "sleepHours"]:
            if candidate in df.columns and "sleeptime" not in df.columns:
                df["sleeptime"] = df[candidate]
                logging.info(f"Normalized sleep field '{candidate}' to 'sleeptime'.")
                break
        # Ensure numeric and clip to 1-24
        if "sleeptime" in df.columns:
            df["sleeptime"] = pd.to_numeric(df["sleeptime"], errors="coerce").fillna(np.nan)
            # leave NaNs to imputer; optionally clip unrealistic values
            df.loc[df["sleeptime"] < 1, "sleeptime"] = np.nan
            df.loc[df["sleeptime"] > 24, "sleeptime"] = np.nan
        return df

    # -----------------------------
    # Prepare DF
    # -----------------------------
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()

            df = self._compute_bmi_if_needed(df)
            df = self._map_gender(df)
            df = self._map_age(df)

            # Map booleans
            for col in ["diffwalk", "physactivity", "alcohol", "smoking"]:
                df = self._map_boolean(df, col)

            df = self._map_stress(df)
            df = self._normalize_sleep_field(df)

            # Drop fields not used
            drop_cols = ["Unnamed: 0", "height", "weight", "hypertension", "highchol", "obesity", "chest_pain", "prior_heart_attack", "heart_disease", "diabetes"]
            df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

            # Ensure target
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
            logging.info("🚀 Starting STROKE data transformation...")

            train_df = self._load_csv(self.data_validation_artifact.valid_train_file_path)
            test_df = self._load_csv(self.data_validation_artifact.valid_test_file_path)

            train_df = self._prepare_dataframe(train_df)
            test_df = self._prepare_dataframe(test_df)

            # Validate required features
            missing = [f for f in self.FINAL_FEATURES if f not in train_df.columns]
            if missing:
                raise AutoCareException(f"Missing required stroke feature(s) in train set: {missing}", sys)

            feature_cols = self.FINAL_FEATURES.copy()

            # Ensure test has same columns
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

            logging.info("✅ STROKE Data Transformation Completed!")
            return artifact

        except Exception as e:
            raise AutoCareException(e, sys)
