# ======================================================
# 🧠 AutoCare Diabetes Model Trainer Component (Updated)
# ======================================================

import os
import sys
import time
import json
import numpy as np
from typing import Dict

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, precision_score, recall_score , accuracy_score

from xgboost import XGBClassifier

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
    ✅ Performs grid search hyperparameter tuning
    ✅ Evaluates using F1-score, precision, recall
    ✅ Logs details for each model
    ✅ Saves best model + preprocessor into 'model_processor' folder
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
            logging.info("📥 Loading transformed train/test arrays...")
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_file_path)

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1].astype(int)
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1].astype(int)

            logging.info(f"📊 Train shape: {X_train.shape}, Test shape: {X_test.shape}")
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
                accuracy_score=float(accuracy_score(y_train, y_train_pred) * 100)  # %

            )

            test_metrics = ClassificationMetricArtifact(
                f1_score=float(f1_score(y_test, y_test_pred)),
                precision_score=float(precision_score(y_test, y_test_pred, zero_division=0)),
                recall_score=float(recall_score(y_test, y_test_pred, zero_division=0)),
                accuracy_score=float(accuracy_score(y_train, y_train_pred) * 100)  # %
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
                "LogisticRegression": LogisticRegression(max_iter=10000, solver="liblinear", random_state=42),
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

            results_summary = {}
            best_model = None
            best_model_name = None
            best_test_f1 = -1.0
            best_train_metrics = None
            best_test_metrics = None

            # -------------------------------
            # Training & Hyperparameter Tuning Loop
            # -------------------------------
            for name, model in models.items():
                logging.info(f"🔹 Starting GridSearchCV for: {name}")
                start_time = time.time()

                grid = GridSearchCV(model, params[name], scoring="f1", cv=3, n_jobs=-1, verbose=0)
                grid.fit(X_train, y_train)
                elapsed = time.time() - start_time

                best_estimator = grid.best_estimator_
                best_params = grid.best_params_
                best_cv_score = grid.best_score_

                logging.info(f"✅ {name} tuning completed in {elapsed:.1f} sec")
                logging.info(f"   🔧 Best Params: {best_params}")
                logging.info(f"   📈 CV Best F1: {best_cv_score:.4f}")

                # Evaluate
                train_metrics, test_metrics = self._evaluate(best_estimator, X_train, y_train, X_test, y_test)
                logging.info(
                    f"   📊 Train F1: {train_metrics.f1_score:.4f}, Test F1: {test_metrics.f1_score:.4f}"
                )

                results_summary[name] = {
                    "cv_best_f1": best_cv_score,
                    "best_params": best_params,
                    "train_f1": train_metrics.f1_score,
                    "test_f1": test_metrics.f1_score,
                    "test_accuracy_percent": test_metrics.accuracy_score,
                    "precision": test_metrics.precision_score,
                    "recall": test_metrics.recall_score,
                    "training_time_sec": elapsed,
                }

                # Track best model
                if test_metrics.f1_score > best_test_f1:
                    best_test_f1 = test_metrics.f1_score
                    best_model = best_estimator
                    best_model_name = name
                    best_train_metrics = train_metrics
                    best_test_metrics = test_metrics

            logging.info("📜 Model Comparison Summary:")
            logging.info(json.dumps(results_summary, indent=2))

            if best_model is None:
                raise Exception("❌ No suitable model found after tuning.")

            logging.info(f"🏆 Best Model: {best_model_name} | Test F1: {best_test_f1:.4f}")

            # ======================================================
            # 🔹 Save best model & preprocessor inside model_processor folder
            # ======================================================
            os.makedirs(self.config.model_dir, exist_ok=True)

            model_path = os.path.join(self.config.model_dir, "model.pkl")
            preprocessor_path = os.path.join(self.config.model_dir, "preprocessor.pkl")

            # Save trained model
            save_object(model_path, best_model)
            logging.info(f"✅ Best model saved at: {model_path}")

            # Load preprocessor from transformation artifact and save copy
            try:
                preprocessor_obj = load_object(
                    self.data_transformation_artifact.transformed_object_file_path
                )
                save_object(preprocessor_path, preprocessor_obj)
                logging.info(f"✅ Preprocessor saved at: {preprocessor_path}")
            except Exception as e:
                logging.warning(f"⚠️ Could not save preprocessor object: {e}")

            # ======================================================
            # 🔹 Also Save Inside Artifacts Folder for Reference
            # ======================================================
            trained_model_path = self.config.trained_model_file_path
            os.makedirs(os.path.dirname(trained_model_path), exist_ok=True)
            save_object(trained_model_path, best_model)
            logging.info(f"📦 Model also stored under artifacts: {trained_model_path}")

            # ======================================================
            # 🔹 Return Training Artifact
            # ======================================================
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=trained_model_path,
                train_metric_artifact=best_train_metrics,
                test_metric_artifact=best_test_metrics,
            )

            logging.info("✅ Model Training Completed Successfully.")
            return model_trainer_artifact

        except Exception as e:
            raise AutoCareException(e, sys)
