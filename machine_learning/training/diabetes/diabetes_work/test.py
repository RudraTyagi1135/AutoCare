# ===========================================================
# 🚀 AutoCare Diabetes Training Pipeline Runner
# ===========================================================

import sys
from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging

# -------- Component Imports --------
from machine_learning.training.diabetes.diabetes_work.components.data_ingestion import DataIngestion
from machine_learning.training.diabetes.diabetes_work.components.data_validation import DataValidation
from machine_learning.training.diabetes.diabetes_work.components.data_transformation import DataTransformation
from machine_learning.training.diabetes.diabetes_work.components.model_trainer import ModelTrainer

# -------- Config Entity Imports --------
from machine_learning.training.diabetes.diabetes_work.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)


def pretty_print(title: str, obj) -> None:
    """Utility for printing artifacts neatly."""
    print("\n" + "=" * 90)
    print(f"🧩 {title}")
    print(obj)
    print("=" * 90 + "\n")


if __name__ == "__main__":
    try:
        logging.info("=" * 90)
        logging.info("🚀 Starting AutoCare Diabetes ML Training Pipeline")
        logging.info("=" * 90)

        # ===========================================================
        # 1️⃣ TRAINING PIPELINE CONFIGURATION
        # ===========================================================
        training_pipeline_config = TrainingPipelineConfig()

        # ===========================================================
        # 2️⃣ DATA INGESTION
        # ===========================================================
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)

        logging.info("📥 Initiating Data Ingestion...")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("✅ Data Ingestion Completed Successfully.")
        pretty_print("Data Ingestion Artifact", data_ingestion_artifact)

        # ===========================================================
        # 3️⃣ DATA VALIDATION
        # ===========================================================
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(
            data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config=data_validation_config
        )

        logging.info("🔍 Initiating Data Validation...")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("✅ Data Validation Completed Successfully.")
        pretty_print("Data Validation Artifact", data_validation_artifact)

        # Stop pipeline if validation failed
        if not getattr(data_validation_artifact, "validation_status", False):
            logging.error("❌ Data validation failed — aborting training pipeline.")
            raise AutoCareException("Data Validation Failed. Check drift report or invalid files.", sys)

        # ===========================================================
        # 4️⃣ DATA TRANSFORMATION
        # ===========================================================
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config
        )

        logging.info("⚙ Initiating Data Transformation...")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("✅ Data Transformation Completed Successfully.")
        pretty_print("Data Transformation Artifact", data_transformation_artifact)

        # ===========================================================
        # 5️⃣ MODEL TRAINER
        # ===========================================================
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact
        )

        logging.info("🤖 Initiating Model Training...")
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("✅ Model Training Completed Successfully.")
        pretty_print("Model Trainer Artifact", model_trainer_artifact)

        # ===========================================================
        # ✅ PIPELINE COMPLETED
        # ===========================================================
        logging.info("=" * 90)
        logging.info("🏁 AutoCare Diabetes Training Pipeline Finished Successfully!")
        logging.info("=" * 90)

    except Exception as e:
        logging.error("❌ Exception occurred during pipeline execution.", exc_info=True)
        raise AutoCareException(e, sys)