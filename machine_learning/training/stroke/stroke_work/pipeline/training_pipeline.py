# ===========================================================
# 🚀 AutoCare Stroke Training Pipeline Runner (Updated)
# ===========================================================

import sys
import os

# ensure artifacts/logs local to stroke work
os.environ["PIPELINE_ROOT"] = "machine_learning/training/stroke/stroke_work"
os.environ["PIPELINE_NAME"] = "stroke"

from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging

# -------- Component Imports (stroke-specific) --------
from machine_learning.training.stroke.stroke_work.components.data_ingestion import DataIngestion
from machine_learning.training.stroke.stroke_work.components.data_validation import DataValidation
from machine_learning.training.stroke.stroke_work.components.data_transformation import DataTransformation
from machine_learning.training.stroke.stroke_work.components.model_trainer import ModelTrainer

# -------- Config Entity Imports (stroke-specific) --------
from machine_learning.training.stroke.stroke_work.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)


# ===========================================================
# 📘 Pretty Print Helper
# ===========================================================
def pretty_print(title: str, obj) -> None:
    """Utility for printing artifacts neatly."""
    print("\n" + "=" * 90)
    print(f"🧩 {title}")
    print(obj)
    print("=" * 90 + "\n")


# ===========================================================
# 🏁 Main Execution
# ===========================================================
if __name__ == "__main__":
    try:
        logging.info("=" * 90)
        logging.info("🚀 Starting AutoCare Stroke ML Training Pipeline")
        logging.info("=" * 90)

        # 1️⃣ TRAINING PIPELINE CONFIGURATION
        training_pipeline_config = TrainingPipelineConfig()
        logging.info("⚙ Training Pipeline Configuration Initialized.")

        # 2️⃣ DATA INGESTION
        logging.info("📥 Initiating Data Ingestion...")
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)

        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("✅ Data Ingestion Completed Successfully.")
        pretty_print("Data Ingestion Artifact", data_ingestion_artifact)

        # 3️⃣ DATA VALIDATION
        logging.info("🔍 Initiating Data Validation...")
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(
            data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config=data_validation_config
        )

        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("✅ Data Validation Completed.")
        pretty_print("Data Validation Artifact", data_validation_artifact)

        # Option C: Log drift but allow training to continue.
        if not getattr(data_validation_artifact, "validation_status", False):
            # Important: Drift report was saved by DataValidation component.
            logging.warning("⚠ Data validation indicated drift or issues. Proceeding with training by design (Option C).")
            logging.warning(f"Drift report path: {data_validation_artifact.drift_report_file_path if hasattr(data_validation_artifact, 'drift_report_file_path') else 'N/A'}")
        else:
            logging.info("✅ Data validation passed (no significant drift detected).")

        # 4️⃣ DATA TRANSFORMATION
        logging.info("⚙ Initiating Data Transformation...")
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config
        )

        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("✅ Data Transformation Completed Successfully.")
        pretty_print("Data Transformation Artifact", data_transformation_artifact)

        # 5️⃣ MODEL TRAINER
        logging.info("🤖 Initiating Model Training...")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact
        )

        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("✅ Model Training Completed Successfully.")
        pretty_print("Model Trainer Artifact", model_trainer_artifact)

        # PIPELINE COMPLETED
        logging.info("=" * 90)
        logging.info("🏁 AutoCare Stroke Training Pipeline Finished Successfully!")
        logging.info("=" * 90)

    except Exception as e:
        # Log full traceback
        logging.exception("❌ Exception occurred during pipeline execution.")
        # Re-raise preserving original exception (wrap only if you need AutoCareException semantics)
        raise
        raise AutoCareException(e, sys) from e