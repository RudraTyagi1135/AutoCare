# ===========================================================
# 🚀 AutoCare Heart Training Pipeline Runner (Milestone-4)
# ===========================================================

import sys
import os

os.environ["PIPELINE_ROOT"] = "machine_learning/training/heart/heart_work"
os.environ["PIPELINE_NAME"] = "heart"

from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging

# -------- Component Imports --------
from machine_learning.training.heart.heart_work.components.data_ingestion import DataIngestion
from machine_learning.training.heart.heart_work.components.data_validation import DataValidation
from machine_learning.training.heart.heart_work.components.data_transformation import DataTransformation
from machine_learning.training.heart.heart_work.components.model_trainer import ModelTrainer

# -------- Config Entity Imports --------
from machine_learning.training.heart.heart_work.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)


def pretty_print(title: str, obj) -> None:
    print("\n" + "=" * 90)
    print(f"🧩 {title}")
    print(obj)
    print("=" * 90 + "\n")


if __name__ == "__main__":
    try:
        logging.info("=" * 90)
        logging.info("🚀 Starting AutoCare Heart Training Pipeline")
        logging.info("=" * 90)

        pipeline_config = TrainingPipelineConfig()

        # 2️⃣ Ingestion
        ingestion = DataIngestion(DataIngestionConfig(pipeline_config))
        ingestion_artifact = ingestion.initiate_data_ingestion()
        pretty_print("Data Ingestion Artifact", ingestion_artifact)

        # 3️⃣ Validation (Option-C)
        validation = DataValidation(
            ingestion_artifact,
            DataValidationConfig(pipeline_config)
        )
        validation_artifact = validation.initiate_data_validation()
        pretty_print("Data Validation Artifact", validation_artifact)

        if not validation_artifact.validation_status:
            logging.warning("⚠ Drift detected — continuing with training (Option-C).")
        else:
            logging.info("✅ Data validation passed.")

        # 4️⃣ Transformation
        transformation = DataTransformation(
            validation_artifact, DataTransformationConfig(pipeline_config)
        )
        transformation_artifact = transformation.initiate_data_transformation()
        pretty_print("Data Transformation Artifact", transformation_artifact)

        # 5️⃣ Model Trainer
        trainer = ModelTrainer(
            ModelTrainerConfig(pipeline_config),
            transformation_artifact
        )
        trainer_artifact = trainer.initiate_model_trainer()
        pretty_print("Model Trainer Artifact", trainer_artifact)

        logging.info("=" * 90)
        logging.info("🏁 AutoCare Heart Training Pipeline Completed")
        logging.info("=" * 90)

    except Exception as e:
        logging.exception("❌ Exception during pipeline execution")
        raise AutoCareException(e, sys)
