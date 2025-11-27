# =============================================== #
#               Stroke Data Transformation
# =============================================== #

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

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
        self.config = data_transformation_config
        self.data_validation_artifact = data_validation_artifact

        self.age_mapping = {
            '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
            '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
            '70-74': 11, '75-79': 12, '80 or older': 13
        }

    def _prepare_dataframe(self, df):
        df = df.copy()

        # Compute BMI if needed
        if "bmi" not in df.columns and {"height", "weight"}.issubset(df.columns):
            df["bmi"] = df["weight"] / ((df["height"] / 100) ** 2)

        # Gender mapping
        df["gender"] = df["gender"].apply(lambda x: 1 if str(x).lower() in ["male", "m"] else 0)

        # -------------------------------
        # FIXED AGE HANDLING LOGIC
        # -------------------------------
        if "age_category" in df.columns:
            df["age_category"] = df["age_category"].map(lambda x: self.age_mapping.get(str(x).strip(), np.nan))

        elif "age" in df.columns:
            def to_bucket(a):
                try:
                    a = float(a)
                except:
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

            df["age_category"] = df["age"].apply(to_bucket)

        else:
            raise AutoCareException(
                "❌ Stroke dataset must contain either 'age_category' or 'age'.",
                sys
            )

        # Boolean value normalization
        for col in ["diffwalk", "physactivity", "alcohol", "smoking"]:
            df[col] = df[col].apply(lambda x: 1 if str(x).lower() in ["1", "yes", "true", "y"] else 0)

        # Stress mapping
        df["stress_category"] = df["stress_category"].map(
            {"no stress": 0, "mild": 1, "moderate": 2, "high": 3, "severe": 4}
        )

        # Normalize sleep field naming if needed
        if "sleeptime" not in df.columns:
            for alt in ["sleep_time", "sleep_hours", "sleepHours"]:
                if alt in df.columns:
                    df["sleeptime"] = df[alt]
                    break

        # Drop unused helper columns
        df.drop(columns=[c for c in ["height", "weight", "Unnamed: 0"] if c in df.columns], inplace=True)

        # Ensure target is integer
        df[self.TARGET_COLUMN] = df[self.TARGET_COLUMN].astype(int)

        return df

    def initiate_data_transformation(self):
        try:
            train_df = self._prepare_dataframe(pd.read_csv(self.data_validation_artifact.valid_train_file_path))
            test_df  = self._prepare_dataframe(pd.read_csv(self.data_validation_artifact.valid_test_file_path))

            missing = [c for c in self.FINAL_FEATURES if c not in train_df.columns]
            if missing:
                raise AutoCareException(f"Missing stroke feature(s): {missing}", sys)

            feature_cols = self.FINAL_FEATURES.copy()

            y_train = train_df[self.TARGET_COLUMN].values
            y_test = test_df[self.TARGET_COLUMN].values

            pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ])

            preprocessor = ColumnTransformer([("numeric", pipeline, feature_cols)])

            X_train_scaled = preprocessor.fit_transform(train_df[feature_cols])
            X_test_scaled = preprocessor.transform(test_df[feature_cols])

            save_object(self.config.transformed_object_file_path, preprocessor)

            train_arr = np.c_[X_train_scaled, y_train]
            test_arr = np.c_[X_test_scaled, y_test]

            save_numpy_array_data(self.config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.config.transformed_test_file_path, test_arr)

            return DataTransformationArtifact(
                transformed_object_file_path=self.config.transformed_object_file_path,
                transformed_train_file_path=self.config.transformed_train_file_path,
                transformed_test_file_path=self.config.transformed_test_file_path,
            )

        except Exception as e:
            raise AutoCareException(e, sys)
