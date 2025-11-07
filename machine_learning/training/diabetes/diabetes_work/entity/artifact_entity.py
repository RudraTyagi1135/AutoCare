# ============================ #
#   ML Pipeline Artifact Classes
# ============================ #

from dataclasses import dataclass

# ============================ #
#   Data Ingestion Artifact
# ============================ #
@dataclass
class DataIngestionArtifact:
    """
    Metadata container for outputs of the Data Ingestion step.

    Attributes:
        trained_file_path (str): Path to the training dataset CSV file.
        test_file_path (str): Path to the testing dataset CSV file.
    """
    trained_file_path: str
    test_file_path: str


# ============================ #
#   Data Validation Artifact
# ============================ #
@dataclass
class DataValidationArtifact:
    """
    Holds metadata and validation results from the Data Validation step.

    Attributes:
        validation_status (bool): True if dataset passed all validation checks.
        valid_train_file_path (str): Path to the validated training dataset.
        valid_test_file_path (str): Path to the validated testing dataset.
        invalid_train_file_path (str): Path to the invalid training dataset.
        invalid_test_file_path (str): Path to the invalid testing dataset.
        drift_report_file_path (str): Path to the data drift report (YAML/JSON).
    """
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str


# ============================ #
#   Data Transformation Artifact
# ============================ #
@dataclass
class DataTransformationArtifact:
    """
    Artifact class for storing outputs of the Data Transformation step.

    Attributes:
        transformed_object_file_path (str): Path to the serialized preprocessing object (scaler/encoder).
        transformed_train_file_path (str): Path to the transformed training dataset (.npy or other format).
        transformed_test_file_path (str): Path to the transformed testing dataset (.npy or other format).
    """
    transformed_object_file_path: str
    transformed_train_file_path: str
    transformed_test_file_path: str


# ============================ #
#   Classification Metric Artifact
# ============================ #
@dataclass
class ClassificationMetricArtifact:
    """
    Stores evaluation metrics for classification tasks.

    Attributes:
        f1_score (float): F1 score for the dataset.
        precision_score (float): Precision score.
        recall_score (float): Recall score.
    """
    f1_score: float
    precision_score: float
    recall_score: float


# ============================ #
#   Model Trainer Artifact
# ============================ #
@dataclass
class ModelTrainerArtifact:
    """
    Artifact container for trained model outputs and performance metrics.

    Attributes:
        trained_model_file_path (str): Path to the saved trained model.
        train_metric_artifact (ClassificationMetricArtifact): Metrics on the training dataset.
        test_metric_artifact (ClassificationMetricArtifact): Metrics on the testing dataset.
    """
    trained_model_file_path: str
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact
