# ============================ #
#   Heart Model Data Transformation
# ============================ #

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging
from machine_learning.training.heart.heart_work.entity.config_entity import DataTransformationConfig
from machine_learning.training.heart.heart_work.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact,
)
from machine_learning.ml_utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:

    TARGET_COLUMN = "heart_disease"

    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact

            self.age_mapping = {
                '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
                '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
                '70-74': 11, '75-79': 12, '80 or older': 13
            }

            logging.info("✅ Heart DataTransformation instance created successfully.")

        except Exception as e:
            raise AutoCareException(e, sys)

    def _load_csv(self, path):
        try:
            df = pd.read_csv(path)
            logging.info(f"Loaded dataset: {path}, Shape: {df.shape}")
            return df
        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Mappings
    # -----------------------------
    def _map_gender(self, df):
        df["gender"] = df["gender"].map(lambda x: 1 if str(x).lower() in ["male", "m"] else 0)
        return df

    def _map_age(self, df):
        df["age_category"] = df["age_category"].map(self.age_mapping)
        return df

    def _compute_bmi(self, df):
        df["bmi"] = df["weight"] / ((df["height"] / 100) ** 2)
        return df

    def _compute_obesity(self, df):
        df["obesity"] = df["bmi"].apply(lambda x: 1 if x > 29 else 0)
        return df

    def _compute_hypertension(self, df):
        df["hypertension"] = df.apply(
            lambda r: 1 if (float(r["systolic"]) >= 130 or float(r["diastolic"]) >= 85) else 0, axis=1)
        return df

    def _map_yes_no(self, df, column):
        df[column] = df[column].apply(lambda x: 1 if str(x).lower() in ["yes", "y", "1", "true"] else 0)
        return df

    def _map_stress(self, df):
        mapping = {"no stress": 0, "mild": 1, "moderate": 2, "high": 3, "severe": 4}
        df["stress_category"] = df["stress_category"].map(lambda x: mapping.get(str(x).lower(), np.nan))
        return df

    # -----------------------------
    # Prepare DF
    # -----------------------------
    def _prepare_dataframe(self, df):
        try:
            df = df.copy()

            df = self._compute_bmi(df)
            df = self._compute_obesity(df)
            df = self._compute_hypertension(df)
            df = self._map_gender(df)
            df = self._map_age(df)
            df = self._map_yes_no(df, "chest_pain")
            df = self._map_yes_no(df, "prior_heart_attack")
            df = self._map_yes_no(df, "smoking")
            df = self._map_yes_no(df, "alcohol")
            df = self._map_yes_no(df, "physactivity")
            df = self._map_yes_no(df, "highchol")
            df = self._map_stress(df)

            drop_cols = ["Unnamed: 0", "height", "weight", "bmi"]
            df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

            df[self.TARGET_COLUMN] = df[self.TARGET_COLUMN].astype(int)

            logging.info(f"Processed DF Columns: {df.columns}")
            return df

        except Exception as e:
            raise AutoCareException(e, sys)

    # -----------------------------
    # Main function
    # -----------------------------
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("🚀 Starting HEART data transformation...")

            train_df = self._load_csv(self.data_validation_artifact.valid_train_file_path)
            test_df = self._load_csv(self.data_validation_artifact.valid_test_file_path)

            train_df = self._prepare_dataframe(train_df)
            test_df = self._prepare_dataframe(test_df)

            # Separate X, y
            feature_cols = [c for c in train_df.columns if c != self.TARGET_COLUMN]

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
            save_object(self.config.transformed_object_file_path, preprocessor)

            train_arr = np.c_[X_train_scaled, y_train]
            test_arr = np.c_[X_test_scaled, y_test]

            save_numpy_array_data(self.config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.config.transformed_test_file_path, test_arr)

            artifact = DataTransformationArtifact(
                transformed_object_file_path=self.config.transformed_object_file_path,
                transformed_train_file_path=self.config.transformed_train_file_path,
                transformed_test_file_path=self.config.transformed_test_file_path,
            )

            logging.info("✅ HEART Data Transformation Completed!")
            return artifact

        except Exception as e:
            raise AutoCareException(e, sys)
