# ================================
# 📦 Basic Imports
# ================================
import os      # For path operations
import sys     # For system-level operations (traceback, etc.)
import numpy as np   # Numerical operations (preprocessing, ML tasks)
import pandas as pd  # Data manipulation & CSV handling


# ================================
# 🎯 Common Constants for Training Pipeline
# ================================
"""
These constants are shared across the entire ML pipeline.
"""

# Column to be predicted by the ML model
TARGET_COLUMN: str = "Result"

# ML pipeline/project name (used in logs, artifact folders, S3 paths)
PIPELINE_NAME: str = "AutoCare"

# Root folder for all pipeline artifacts (data, models, logs, reports)
ARTIFACT_DIR: str = "Artifacts"

# Raw dataset filename
FILE_NAME: str = "Heart_73733 _Final_data.xlsx"

# Output filenames for train/test splits
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

# Path to the YAML schema file defining the dataset structure
SCHEMA_FILE_PATH: str = os.path.join("data_schema", "schema.yaml")

SAVED_MODEL_DIR = os.path.join("saved_models")
MODEL_FILE_NAME = "model.pkl"



# ================================
# 💾 Data Ingestion Related Constants
# ================================
"""
Constants specific to the Data Ingestion stage.
"""

# MongoDB configuration
DATA_INGESTION_COLLECTION_NAME: str = "heart_raw"
DATA_INGESTION_DATABASE_NAME: str = "Heart"

# Folder structure within artifacts for data ingestion
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "raw_data"  # Raw snapshot of dataset
DATA_INGESTION_INGESTED_DIR: str = "ingested"           # Split train/test datasets

# Train/Test split ratio
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2  # 20% test, 80% train


# ================================
# 💾 Data Validation Related Constants
# ================================
"""
Constants specific to Data Validation stage.
"""

# Folder structure for data validation artifacts
DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_VALID_DIR: str = "validated"         # Valid data
DATA_VALIDATION_INVALID_DIR: str = "invalid"         # Invalid/rejected data
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_store"  # Data drift reports

# Filename for the data drift report
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"


# ================================
# 💾 Data Transformation Related Constants
# ================================
"""
Constants specific to Data Transformation stage.
"""

# Folder structure for transformation artifacts
DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR: str = "transformed"          # Transformed datasets (.npy)
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR: str = "transformed_object" # Preprocessing objects (scalers, encoders, etc.)

# Imputer parameters for missing values
DATA_TRANSFORMATION_IMPUTER_PARAMS: dict = {
    "missing_values": np.nan,
    "n_neighbors": 3,
    "weights": "uniform",
}

# File paths for transformed train/test numpy arrays
DATA_TRANSFORMATION_TRAIN_FILE_PATH: str = "train.npy"
DATA_TRANSFORMATION_TEST_FILE_PATH: str = "test.npy"

PREPROCESSING_OBJECT_FILE_NAME = "preprocessing.pkl"


# ================================
# 🤖 Model Trainer Related Constants
# ================================
"""
Constants specific to the Model Training stage.
"""

# Folder structure for model trainer artifacts
MODEL_TRAINER_DIR_NAME: str = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR: str = "trained_model"
MODEL_TRAINER_TRAINED_MODEL_NAME: str = "model.pkl"

# Model performance expectations
MODEL_TRAINER_EXPECTED_SCORE: float = 0.6  # Minimum accuracy threshold
MODEL_TRAINER_OVERFITTING_UNDERFITTING_THRESHOLD: float = 0.05  # Max acceptable train/test deviation


# ================================
# ☁️ Cloud / Deployment Related Constants
# ================================
"""
Constants for cloud storage and deployment.
"""

# S3 bucket name for storing artifacts and trained models
TRAINING_BUCKET_NAME: str = "Autocare_heart_bucket"
