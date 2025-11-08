# ======================================================
# 🧠 AutoCare Diabetes Model Trainer Component
# ======================================================

import os
import sys
import numpy as np
from typing import Dict

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, precision_score, recall_score

from xgboost import XGBClassifier  # ✅ Added for better performance

from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging

from machine_learning.training.diabetes.diabetes_work.entity.config_entity import ModelTrainerConfig
from machine_learning.training.diabetes.diabetes_work.entity.artifact_entity import (
    ModelTrainerArtifact,
    DataTransformationArtifact,
    ClassificationMetricArtifact,
)
from machine_learning.ml_utils.main_utils.utils import (
    load_object,
    save_object,
    load_numpy_array_data,
)


class ModelTrainer:
    """
    Trains multiple ML models for diabetes classification:
    - Performs grid search hyperparameter tuning
    - Evaluates on F1-score, precision, recall
    - Saves the best model
    - Returns ModelTrainerArtifact
    """

    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact,
    ):
        try:
            self.config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            logging.info("✅ ModelTrainer instance created successfully.")
        except Exception as e:
            raise AutoCareException(e, sys)

    # ======================================================
    # 🔹 Step 1: Load transformed numpy arrays
    # ======================================================
    def _load_data(self):
        try:
            logging.info("Loading transformed train/test arrays...")
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_file_path)

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1].astype(int)
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1].astype(int)

            logging.info(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
            return X_train, y_train, X_test, y_test

        except Exception as e:
            raise AutoCareException(e, sys)

    # ======================================================
    # 🔹 Step 2: Evaluate model metrics (train/test)
    # ======================================================
    def _evaluate(self, model, X_train, y_train, X_test, y_test):
        try:
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_metrics = ClassificationMetricArtifact(
                f1_score=float(f1_score(y_train, y_train_pred)),
                precision_score=float(precision_score(y_train, y_train_pred, zero_division=0)),
                recall_score=float(recall_score(y_train, y_train_pred, zero_division=0)),
            )

            test_metrics = ClassificationMetricArtifact(
                f1_score=float(f1_score(y_test, y_test_pred)),
                precision_score=float(precision_score(y_test, y_test_pred, zero_division=0)),
                recall_score=float(recall_score(y_test, y_test_pred, zero_division=0)),
            )

            return train_metrics, test_metrics
        except Exception as e:
            raise AutoCareException(e, sys)

    # ======================================================
    # 🔹 Step 3: Train & Select Best Model
    # ======================================================
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info("🚀 Initiating Model Training Process...")
            X_train, y_train, X_test, y_test = self._load_data()

            # -------------------------------
            # Candidate models
            # -------------------------------
            models: Dict[str, object] = {
                "LogisticRegression": LogisticRegression(max_iter=1000, solver="liblinear", random_state=42),
                "RandomForest": RandomForestClassifier(random_state=42, n_jobs=-1),
                "GradientBoosting": GradientBoostingClassifier(random_state=42),
                "XGBoost": XGBClassifier(
                    eval_metric="logloss", use_label_encoder=False, n_jobs=-1, random_state=42
                ),
            }

            # -------------------------------
            # Hyperparameter grids
            # -------------------------------
            params: Dict[str, dict] = {
                "LogisticRegression": {"C": [0.01, 0.1, 1.0, 10.0]},
                "RandomForest": {"n_estimators": [100, 200], "max_depth": [5, 10, None]},
                "GradientBoosting": {"n_estimators": [100, 200], "learning_rate": [0.01, 0.1]},
                "XGBoost": {"n_estimators": [100, 200], "learning_rate": [0.01, 0.1], "max_depth": [3, 5, 7]},
            }

            # -------------------------------
            # Training loop
            # -------------------------------
            best_model = None
            best_model_name = None
            best_test_f1 = -1.0
            best_train_metrics = None
            best_test_metrics = None

            for name, model in models.items():
                logging.info(f"🔹 Training model: {name}")
                grid = GridSearchCV(model, params[name], scoring="f1", cv=3, n_jobs=-1, verbose=1)
                grid.fit(X_train, y_train)
                candidate_model = grid.best_estimator_

                train_metrics, test_metrics = self._evaluate(candidate_model, X_train, y_train, X_test, y_test)
                logging.info(
                    f"{name} | Train F1: {train_metrics.f1_score:.4f} | Test F1: {test_metrics.f1_score:.4f}"
                )

                if test_metrics.f1_score > best_test_f1:
                    best_test_f1 = test_metrics.f1_score
                    best_model = candidate_model
                    best_model_name = name
                    best_train_metrics = train_metrics
                    best_test_metrics = test_metrics

            if best_model is None:
                raise Exception("❌ No suitable model found.")

            logging.info(f"🏆 Best Model: {best_model_name} | Test F1: {best_test_f1:.4f}")

            # -------------------------------
            # Save the best model
            # -------------------------------
            trained_model_path = self.config.trained_model_file_path
            os.makedirs(os.path.dirname(trained_model_path), exist_ok=True)
            save_object(trained_model_path, best_model)

            # Also save under final_model for deployment
            os.makedirs("final_model", exist_ok=True)
            save_object(os.path.join("final_model", "diabetes_model.pkl"), best_model)

            logging.info(f"✅ Best model saved at: {trained_model_path}")

            # -------------------------------
            # Return artifact
            # -------------------------------
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=trained_model_path,
                train_metric_artifact=best_train_metrics,
                test_metric_artifact=best_test_metrics,
            )

            logging.info("✅ Model Training Completed Successfully.")
            return model_trainer_artifact

        except Exception as e:
            raise AutoCareException(e, sys)