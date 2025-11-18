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

    TARGET_COLUMN = "stroke"

    # ======================================
    # Stroke uses these features ONLY
    # ======================================
    REQUIRED_FEATURES = [
        "gender",
        "age_category",
        "bmi",
        "diabetes",
        "heart_disease",
        "sleep_time",
        "diffwalk",
        "physactivity",
        "alcohol",
        "smoking",
        "stress_category",
    ]

    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact

            # age mapping
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

    def _map_gender(self, df):
        if "gender" in df.columns:
            df["gender"] = df["gender"].map(lambda x: 1 if str(x).lower() in ["male", "m"] else 0)
        return df

    def _map_age_category(self, df):
        if "age_category" in df.columns:
            df["age_category"] = df["age_category"].map(
                lambda x: self.age_mapping.get(str(x).strip(), np.nan)
            )
        return df

    def _map_boolean(self, df, col):
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: 1 if str(x).lower() in ["yes", "y", "1", "true"] else 0
            )
        return df

    def _map_stress(self, df):
        if "stress_category" in df.columns:
            mapping = {
                "no stress": 0, "mild": 1, "moderate": 2, "high": 3, "severe": 4
            }
            df["stress_category"] = df["stress_category"].map(
                lambda x: mapping.get(str(x).lower(), np.nan)
            )
        return df

    # -----------------------------
    # Main DF Preparation
    # -----------------------------
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()

            # convert categorical → numeric
            df = self._map_gender(df)
            df = self._map_age_category(df)

            df = self._map_boolean(df, "diffwalk")
            df = self._map_boolean(df, "physactivity")
            df = self._map_boolean(df, "alcohol")
            df = self._map_boolean(df, "smoking")

            df = self._map_stress(df)

            # Ensure target is integer
            if self.TARGET_COLUMN in df.columns:
                df[self.TARGET_COLUMN] = df[self.TARGET_COLUMN].astype(int)

            # Drop unused columns safely
            drop_cols = [
                "Unnamed: 0",
                "height",
                "weight",
                "hypertension",
                "highchol",
                "obesity",
                "chest_pain",
                "prior_heart_attack"
            ]
            df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

            logging.info(f"Processed DF Columns: {list(df.columns)}")
            return df

        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Transformation pipeline
    # -----------------------------
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("🚀 Starting STROKE data transformation...")

            # Load validated data
            train_df = self._load_csv(self.data_validation_artifact.valid_train_file_path)
            test_df = self._load_csv(self.data_validation_artifact.valid_test_file_path)

            # Clean + encode
            train_df = self._prepare_dataframe(train_df)
            test_df = self._prepare_dataframe(test_df)

            # Final feature list (exclude target)
            feature_cols = [c for c in self.REQUIRED_FEATURES if c in train_df.columns]

            # Separate X, y
            X_train = train_df[feature_cols].values
            y_train = train_df[self.TARGET_COLUMN].values

            X_test = test_df[feature_cols].values
            y_test = test_df[self.TARGET_COLUMN].values

            # Missing values
            imputer = SimpleImputer(strategy="median")
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            # Scaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Save preprocessor
            preprocessor = {
                "imputer": imputer,
                "scaler": scaler,
                "feature_columns": feature_cols
            }

            save_object(self.config.transformed_object_file_path, preprocessor)
            logging.info(f"Preprocessor saved at: {self.config.transformed_object_file_path}")

            # Combine features + target
            train_arr = np.c_[X_train_scaled, y_train]
            test_arr = np.c_[X_test_scaled, y_test]

            save_numpy_array_data(self.config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.config.transformed_test_file_path, test_arr)

            artifact = DataTransformationArtifact(
                transformed_object_file_path=self.config.transformed_object_file_path,
                transformed_train_file_path=self.config.transformed_train_file_path,
                transformed_test_file_path=self.config.transformed_test_file_path,
            )

            logging.info("✅ STROKE Data Transformation Completed!")
            return artifact

        except Exception as e:
            raise AutoCareException(e, sys)