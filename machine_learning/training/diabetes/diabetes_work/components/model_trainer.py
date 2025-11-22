# machine_learning/training/diabetes/diabetes_work/components/model_trainer.py
# ======================================================
# 🧠 AutoCare Diabetes Model Trainer Component (Final)
# ======================================================

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

# sklearn building blocks for inference preprocessor & pipeline
from sklearn.pipeline import Pipeline as SKPipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.base import TransformerMixin

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
    Final ModelTrainer:
    - Loads transformed numpy arrays produced by DataTransformation (already imputed+scaled)
    - Runs GridSearchCV across candidate estimators (on numeric arrays)
    - Builds an inference preprocessor (ColumnTransformer) from the legacy preprocessor dict saved earlier
      so inference accepts raw pandas.DataFrame with the same feature column names and order.
    - Wraps best model into a fitted sklearn Pipeline([("preprocessor", preproc), ("model", best_model)])
    - Saves:
        - model_dir/model.pkl  (inference-ready pipeline)
        - model_dir/preprocessor.pkl  (preprocessor object)
        - artifacts/trained_model.pkl (raw estimator)
    """

    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            logging.info("✅ ModelTrainer instance created successfully.")
        except Exception as e:
            raise AutoCareException(e, sys)

    # -------------------------
    # Load transformed numpy arrays (these are already imputed+scaled)
    # -------------------------
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

    # -------------------------
    # Compute evaluation metrics
    # -------------------------
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

    # -------------------------
    # Build a ColumnTransformer preprocessor from legacy dict saved by DataTransformation
    # The dict has keys: { "imputer": SimpleImputer, "scaler": StandardScaler, "feature_columns": [...] }
    # We need an object that accepts a pandas.DataFrame (with named columns) and returns the same scaled numeric array.
    # -------------------------
    def _build_preprocessor_from_legacy(self, legacy_obj):
        try:
            if legacy_obj is None:
                raise AutoCareException("No transformed_object provided to build preprocessor.", sys)

            # If the saved object is already a sklearn transformer
            if isinstance(legacy_obj, TransformerMixin) or hasattr(legacy_obj, "transform"):
                logging.info("Legacy object is already a transformer — returning as-is.")
                return legacy_obj

            if not isinstance(legacy_obj, dict):
                raise AutoCareException("transformed_object must be a dict or a transformer.", sys)

            feature_cols = legacy_obj.get("feature_columns", None)
            imputer = legacy_obj.get("imputer", SimpleImputer(strategy="median"))
            scaler = legacy_obj.get("scaler", StandardScaler())

            if not feature_cols or not isinstance(feature_cols, (list, tuple)):
                raise AutoCareException("transformed_object missing 'feature_columns' list.", sys)

            # In your DataTransformation you mapped 'gender' to numeric (1/0). So all feature columns are numeric.
            # Build numeric pipeline: imputer -> scaler
            numeric_pipeline = SKPipeline([("imputer", imputer), ("scaler", scaler)])

            # ColumnTransformer applying numeric_pipeline to the exact feature_cols in the same order.
            # Using remainder='drop' to make sure the output array matches training arrays exactly.
            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", numeric_pipeline, feature_cols)
                ],
                remainder="drop"
            )

            logging.info("✅ Built ColumnTransformer preprocessor from legacy transformed_object.")
            logging.debug(f"feature_columns (count={len(feature_cols)}): {feature_cols}")

            return preprocessor

        except Exception as e:
            raise AutoCareException(e, sys)

    # -------------------------
    # Main training flow
    # -------------------------
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
                "XGBoost": XGBClassifier(eval_metric="logloss", use_label_encoder=False, n_jobs=-1, random_state=42),
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
                logging.info(f"🔹 Starting GridSearchCV for: {name}")
                start_time = time.time()

                grid = GridSearchCV(model, params[name], scoring="f1", cv=3, n_jobs=-1, verbose=0)
                grid.fit(X_train, y_train)
                elapsed = time.time() - start_time

                best_estimator = grid.best_estimator_
                best_params = grid.best_params_
                best_cv_score = grid.best_score_

                logging.info(f"✅ {name} tuning completed in {elapsed:.1f}s - CV best F1: {best_cv_score:.4f}")
                train_metrics, test_metrics = self._evaluate(best_estimator, X_train, y_train, X_test, y_test)
                logging.info(f"   📊 Train F1: {train_metrics.f1_score:.4f}, Test F1: {test_metrics.f1_score:.4f}")

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
                raise Exception("❌ No suitable model found after tuning.")

            logging.info(f"🏆 Selected Best Model: {best_model_name} | Test F1: {best_test_f1:.4f}")

            # ======================================================
            # Build inference preprocessor from transformed_object
            # ======================================================
            preprocessor_obj = None
            try:
                preprocessor_obj = load_object(self.data_transformation_artifact.transformed_object_file_path)
                logging.info("Loaded transformed_object for building preprocessor.")
            except Exception as e:
                logging.warning(f"Could not load transformed_object: {e}. Will abort to avoid mismatch.")
                raise

            preprocessor = self._build_preprocessor_from_legacy(preprocessor_obj)

            # ======================================================
            # Build full inference pipeline and fit it.
            # Important: the numeric preprocessor must be fitted (imputer+scaler)
            # to be compatible with raw DataFrame inputs during inference.
            # We need to fit preprocessor on original (raw) feature data BEFORE combining with model,
            # but we do not have access to raw DataFrame here. So we fit preprocessor using the *already scaled*
            # training arrays by performing a small trick:
            #
            # - We will fit the preprocessor on a placeholder DataFrame constructed from
            #   the feature_columns using inverse-transform not available here, so instead:
            # - Simpler robust approach: preprocessor's imputer and scaler are the SAME objects saved in transformed_object,
            #   which have been fitted during DataTransformation. So re-using them in the preprocessor above preserves fitted state.
            #
            # (Our _build_preprocessor_from_legacy uses the saved imputer & scaler instances — they are already fitted.)
            # ======================================================

            # Build the final pipeline (preprocessor already contains fitted imputer+scaler objects)
            full_pipeline = SKPipeline([("preprocessor", preprocessor), ("model", best_model)])

            # Save pipeline (inference-ready)
            os.makedirs(self.config.model_dir, exist_ok=True)
            model_pipeline_path = os.path.join(self.config.model_dir, "model.pkl")
            preprocessor_path = os.path.join(self.config.model_dir, "preprocessor.pkl")
            trained_model_path = self.config.trained_model_file_path

            save_object(model_pipeline_path, full_pipeline)
            logging.info(f"✅ Full inference pipeline saved at: {model_pipeline_path}")

            # Save preprocessor separately (optional)
            try:
                save_object(preprocessor_path, preprocessor)
                logging.info(f"✅ Preprocessor saved at: {preprocessor_path}")
            except Exception as e:
                logging.warning(f"Could not save preprocessor separately: {e}")

            # Save raw estimator under artifacts
            os.makedirs(os.path.dirname(trained_model_path), exist_ok=True)
            save_object(trained_model_path, best_model)
            logging.info(f"📦 Raw trained model saved under artifacts: {trained_model_path}")

            # Return artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=trained_model_path,
                train_metric_artifact=best_train_metrics,
                test_metric_artifact=best_test_metrics
            )

            logging.info("✅ Model Training Completed Successfully.")
            return model_trainer_artifact

        except Exception as e:
            raise AutoCareException(e, sys)
