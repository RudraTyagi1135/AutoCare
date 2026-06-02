# machine_learning/training/stroke/stroke_work/components/model_trainer.py
import os
import sys
import time
import json
from typing import Dict

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.pipeline import Pipeline as SKPipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.base import TransformerMixin

from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging

from machine_learning.training.stroke.stroke_work.entity.config_entity import ModelTrainerConfig
from machine_learning.training.stroke.stroke_work.entity.artifact_entity import (
    ModelTrainerArtifact,
    DataTransformationArtifact,
    ClassificationMetricArtifact,
)
from machine_learning.ml_utils.main_utils.utils import load_object, save_object, load_numpy_array_data


class ModelTrainer:
    """
    Stroke Model Trainer — consistent implementation to Diabetes/Heart trainers.
    """

    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            logging.info("✅ Stroke ModelTrainer created.")
        except Exception as e:
            raise AutoCareException(e, sys)

    def _load_data(self):
        try:
            logging.info("📥 Loading transformed arrays...")
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_file_path)

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1].astype(int)
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1].astype(int)

            logging.info(f"📊 Train shape: {X_train.shape}, Test shape: {X_test.shape}")
            return X_train, y_train, X_test, y_test
        except Exception as e:
            raise AutoCareException(e, sys)

    def _evaluate(self, model, X_train, y_train, X_test, y_test):
        try:
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_metrics = ClassificationMetricArtifact(
                f1_score=float(f1_score(y_train, y_train_pred)),
                precision_score=float(precision_score(y_train, y_train_pred, zero_division=0)),
                recall_score=float(recall_score(y_train, y_train_pred, zero_division=0)),
                accuracy_score=float(accuracy_score(y_train, y_train_pred) * 100),
            )

            test_metrics = ClassificationMetricArtifact(
                f1_score=float(f1_score(y_test, y_test_pred)),
                precision_score=float(precision_score(y_test, y_test_pred, zero_division=0)),
                recall_score=float(recall_score(y_test, y_test_pred, zero_division=0)),
                accuracy_score=float(accuracy_score(y_test, y_test_pred) * 100),
            )

            return train_metrics, test_metrics
        except Exception as e:
            raise AutoCareException(e, sys)

    def _build_preprocessor_from_legacy(self, legacy_obj):
        try:
            if legacy_obj is None:
                raise AutoCareException("No transformed_object provided.", sys)

            if isinstance(legacy_obj, TransformerMixin) or hasattr(legacy_obj, "transform"):
                logging.info("Legacy object is transformer — returning it.")
                return legacy_obj

            if not isinstance(legacy_obj, dict):
                raise AutoCareException("transformed_object must be a dict or transformer.", sys)

            feature_cols = legacy_obj.get("feature_columns", None)
            imputer = legacy_obj.get("imputer", SimpleImputer(strategy="median"))
            scaler = legacy_obj.get("scaler", StandardScaler())

            if not feature_cols or not isinstance(feature_cols, (list, tuple)):
                raise AutoCareException("transformed_object missing 'feature_columns' list.", sys)

            numeric_pipeline = SKPipeline([("imputer", imputer), ("scaler", scaler)])
            preprocessor = ColumnTransformer(transformers=[("num", numeric_pipeline, feature_cols)], remainder="drop")
            logging.info("✅ Built ColumnTransformer from transformed_object.")
            return preprocessor
        except Exception as e:
            raise AutoCareException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info("🚀 Starting Stroke model training...")
            X_train, y_train, X_test, y_test = self._load_data()

            models: Dict[str, object] = {
                "LogisticRegression": LogisticRegression(max_iter=10000, solver="liblinear", random_state=42),
                "RandomForest": RandomForestClassifier(random_state=42, n_jobs=-1),
                "GradientBoosting": GradientBoostingClassifier(random_state=42),
                "XGBoost": XGBClassifier(eval_metric="logloss", n_jobs=-1, random_state=42),
            }

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

            for name, model in models.items():
                logging.info(f"🔹 GridSearchCV for {name}")
                start_time = time.time()
                grid = GridSearchCV(model, params[name], scoring="f1", cv=3, n_jobs=-1, verbose=0)
                grid.fit(X_train, y_train)
                elapsed = time.time() - start_time

                best_estimator = grid.best_estimator_
                best_params = grid.best_params_
                best_cv_score = grid.best_score_

                train_metrics, test_metrics = self._evaluate(best_estimator, X_train, y_train, X_test, y_test)
                logging.info(f"   {name} | CV F1: {best_cv_score:.4f} | Train F1: {train_metrics.f1_score:.4f} | Test F1: {test_metrics.f1_score:.4f}")

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

                if test_metrics.f1_score > best_test_f1:
                    best_test_f1 = test_metrics.f1_score
                    best_model = best_estimator
                    best_model_name = name
                    best_train_metrics = train_metrics
                    best_test_metrics = test_metrics

            logging.info("📜 Model Comparison Summary:")
            logging.info(json.dumps(results_summary, indent=2))

            if best_model is None:
                raise AutoCareException("No suitable model found after tuning.", sys)

            logging.info(f"🏆 Best Model: {best_model_name} | Test F1: {best_test_f1:.4f}")

            # Build preprocessor
            try:
                preprocessor_obj = load_object(self.data_transformation_artifact.transformed_object_file_path)
            except Exception as e:
                raise AutoCareException(f"Failed loading transformed_object: {e}", sys)

            preprocessor = self._build_preprocessor_from_legacy(preprocessor_obj)

            # Final pipeline
            full_pipeline = SKPipeline([("preprocessor", preprocessor), ("model", best_model)])

            os.makedirs(self.config.model_dir, exist_ok=True)
            model_pipeline_path = os.path.join(self.config.model_dir, "model.pkl")
            preprocessor_path = os.path.join(self.config.model_dir, "preprocessor.pkl")
            trained_model_path = self.config.trained_model_file_path

            save_object(model_pipeline_path, full_pipeline)
            logging.info(f"✅ Inference pipeline saved: {model_pipeline_path}")

            try:
                save_object(preprocessor_path, preprocessor)
                logging.info(f"✅ Preprocessor saved: {preprocessor_path}")
            except Exception as e:
                logging.warning(f"Could not save preprocessor separately: {e}")

            os.makedirs(os.path.dirname(trained_model_path), exist_ok=True)
            save_object(trained_model_path, best_model)
            logging.info(f"📦 Raw estimator saved: {trained_model_path}")

            return ModelTrainerArtifact(
                trained_model_file_path=trained_model_path,
                train_metric_artifact=best_train_metrics,
                test_metric_artifact=best_test_metrics,
            )

        except Exception as e:
            raise AutoCareException(e, sys)
        finally:
            logging.info("✅ Stroke Model training completed.") 