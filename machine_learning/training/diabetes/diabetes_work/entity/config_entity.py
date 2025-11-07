# ================================
# 📦 Imports
# ================================
from datetime import datetime  # For generating timestamps for artifact folders
import os                     # For directory and path operations
from machine_learning.training.diabetes.diabetes_work.constant.training_pipeline import constant# Import your constants file


# ================================
# ⚙️ Training Pipeline Configuration
# ================================
class TrainingPipelineConfig:
    """
    Configuration for the overall ML training pipeline.

    Responsibilities:
    - Store the pipeline name and artifact root directory.
    - Generate timestamped directories for each pipeline run to ensure reproducibility.

    Attributes:
    ----------
    pipeline_name : str
        Name of the pipeline (used in logging, artifact naming).
    artifact_name : str
        Root folder name for all artifacts.
    artifact_dir : str
        Full path to the artifact folder for this run.
    timestamp : str
        Timestamp string used for folder naming and logging.
    """

    def __init__(self, timestamp: datetime = datetime.now()):
        # Convert timestamp to string format suitable for folder names
        timestamp_str = timestamp.strftime("%d_%m_%Y_%H_%M_%S")

        # Pipeline name from constants
        self.pipeline_name: str = constant.PIPELINE_NAME

        # Root artifact folder from constants
        self.artifact_name: str = constant.ARTIFACT_DIR

        # Full artifact directory path for this pipeline run
        self.artifact_dir: str = os.path.join(self.artifact_name, timestamp_str)

        self.model_dir=os.path.join("final_model")

        # Timestamp string for logging, reports, and model versioning
        self.timestamp: str = timestamp_str


# ================================
# ⚙️ Data Ingestion Configuration
# ================================
class DataIngestionConfig:
    """
    Configuration for the Data Ingestion stage.

    Responsibilities:
    - Define paths for raw, training, and testing datasets.
    - Provide MongoDB collection and database names.
    - Maintain a train/test split ratio for reproducibility.

    Attributes:
    ----------
    data_ingestion_dir : str
        Base directory for ingestion artifacts.
    feature_store_file_path : str
        Path to save raw dataset snapshot.
    training_file_path : str
        Path to save split training dataset.
    testing_file_path : str
        Path to save split testing dataset.
    train_test_split_ratio : float
        Ratio for train/test split.
    collection_name : str
        MongoDB collection name for raw data.
    database_name : str
        MongoDB database name.
    """

    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        # Base directory for data ingestion artifacts
        self.data_ingestion_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            constant.DATA_INGESTION_DIR_NAME
        )

        # Path to save raw feature store (original dataset)
        self.feature_store_file_path: str = os.path.join(
            self.data_ingestion_dir,
            constant.DATA_INGESTION_FEATURE_STORE_DIR,
            constant.FILE_NAME
        )

        # Paths for train/test split files
        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir,
            constant.DATA_INGESTION_INGESTED_DIR,
            constant.TRAIN_FILE_NAME
        )
        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir,
            constant.DATA_INGESTION_INGESTED_DIR,
            constant.TEST_FILE_NAME
        )

        # Train/test split ratio
        self.train_test_split_ratio: float = constant.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO

        # MongoDB settings
        self.collection_name: str = constant.DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = constant.DATA_INGESTION_DATABASE_NAME


# ================================
# ⚙️ Data Validation Configuration
# ================================
class DataValidationConfig:
    """
    Configuration for the Data Validation stage.

    Responsibilities:
    - Define directories and file paths for validated and invalid data.
    - Define path for the data drift report.

    Attributes:
    ----------
    data_validation_dir : str
        Root folder for data validation artifacts.
    valid_data_dir : str
        Folder for storing valid train/test datasets.
    invalid_data_dir : str
        Folder for storing invalid/rejected train/test datasets.
    valid_train_file_path : str
        Path to save validated training dataset.
    valid_test_file_path : str
        Path to save validated testing dataset.
    invalid_train_file_path : str
        Path to save invalid training dataset.
    invalid_test_file_path : str
        Path to save invalid testing dataset.
    drift_report_file_path : str
        Path to save dataset drift report.
    """

    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        # Root folder for all data validation artifacts
        self.data_validation_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            constant.DATA_VALIDATION_DIR_NAME
        )

        # Directories for valid and invalid data
        self.valid_data_dir: str = os.path.join(
            self.data_validation_dir,
            constant.DATA_VALIDATION_VALID_DIR
        )
        self.invalid_data_dir: str = os.path.join(
            self.data_validation_dir,
            constant.DATA_VALIDATION_INVALID_DIR
        )

        # Valid dataset file paths
        self.valid_train_file_path: str = os.path.join(
            self.valid_data_dir,
            constant.TRAIN_FILE_NAME
        )
        self.valid_test_file_path: str = os.path.join(
            self.valid_data_dir,
            constant.TEST_FILE_NAME
        )

        # Invalid dataset file paths
        self.invalid_train_file_path: str = os.path.join(
            self.invalid_data_dir,
            constant.TRAIN_FILE_NAME
        )
        self.invalid_test_file_path: str = os.path.join(
            self.invalid_data_dir,
            constant.TEST_FILE_NAME
        )

        # Data drift report path
        self.drift_report_file_path: str = os.path.join(
            self.data_validation_dir,
            constant.DATA_VALIDATION_DRIFT_REPORT_DIR,
            constant.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
        )


# ================================
# ⚙️ Data Transformation Configuration
# ================================
class DataTransformationConfig:
    """
    Configuration for Data Transformation stage.

    Responsibilities:
    - Define directories for transformed datasets and preprocessing objects.
    - Ensure proper file naming and directory structure.

    Attributes:
    ----------
    data_transformation_dir : str
        Root directory for transformation artifacts.
    transformed_train_file_path : str
        Path to save transformed training dataset (.npy format).
    transformed_test_file_path : str
        Path to save transformed testing dataset (.npy format).
    transformed_object_file_path : str
        Path to save preprocessing object (scaler/encoder/etc.).
    """

    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_transformation_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            constant.DATA_TRANSFORMATION_DIR_NAME
        )
        self.transformed_train_file_path: str = os.path.join(
            self.data_transformation_dir,
            constant.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            constant.TRAIN_FILE_NAME.replace("csv", "npy")
        )
        self.transformed_test_file_path: str = os.path.join(
            self.data_transformation_dir,
            constant.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            constant.TEST_FILE_NAME.replace("csv", "npy")
        )
        self.transformed_object_file_path: str = os.path.join(
            self.data_transformation_dir,
            constant.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR,
            constant.PREPROCESSING_OBJECT_FILE_NAME
        )


# ================================
# ⚙️ Model Trainer Configuration
# ================================
class ModelTrainerConfig:
    """
    Configuration for the Model Training stage.

    Responsibilities:
    - Define directory paths for saving trained models.
    - Set expected accuracy and overfitting/underfitting thresholds.

    Attributes:
    ----------
    model_trainer_dir : str
        Root folder for model training artifacts.
    trained_model_file_path : str
        Path to save the trained model.
    expected_accuracy : float
        Minimum acceptable model accuracy for deployment.
    overfitting_underfitting_threshold : float
        Maximum allowed deviation between training and testing accuracy.
    """

    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.model_trainer_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            constant.MODEL_TRAINER_DIR_NAME
        )
        self.trained_model_file_path: str = os.path.join(
            self.model_trainer_dir,
            constant.MODEL_TRAINER_TRAINED_MODEL_DIR,
            constant.MODEL_TRAINER_TRAINED_MODEL_NAME
        )
        self.expected_accuracy: float = constant.MODEL_TRAINER_EXPECTED_SCORE
        self.overfitting_underfitting_threshold: float = constant.MODEL_TRAINER_OVERFITTING_UNDERFITTING_THRESHOLD


