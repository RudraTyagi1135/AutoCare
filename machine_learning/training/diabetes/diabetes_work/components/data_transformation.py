# Imports
import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from diabetes_work.constant.training_pipeline.constant import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from diabetes_work.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from diabetes_work.entity.config_entity import DataTransformationConfig
from autocare_utils.exception import AutoCareException  # Custom exception handling
from autocare_utils.logging import logging
from ml_utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    """
    Class for performing data transformation operations including:
    - Reading validated CSV datasets
    - Applying preprocessing pipelines (e.g., KNN imputation)
    - Saving transformed datasets and preprocessing objects
    """

    def __init__(self, 
                 data_validation_artifact: DataValidationArtifact, 
                 data_transformation_config: DataTransformationConfig):
        """
        Initializes the DataTransformation object with required artifacts and configs.
        
        Args:
            data_validation_artifact (DataValidationArtifact): Artifact containing validated train/test file paths
            data_transformation_config (DataTransformationConfig): Configuration for data transformation
        
        Raises:
            NetworkSecurityException: If initialization fails
        """
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_tranformation_config = data_transformation_config
        except Exception as e:
            raise AutoCareException(e, sys)
        

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """
        Reads a CSV file into a pandas DataFrame.

        Args:
            file_path (str): Path to the CSV file

        Returns:
            pd.DataFrame: Loaded dataframe
        
        Raises:
            NetworkSecurityException: If reading the file fails
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise AutoCareException(e, sys)
        

    def get_data_transformer_object(cls) -> Pipeline:  # type: ignore
        """
        Creates and returns a preprocessing pipeline for transforming input features.
        Currently, it applies KNN imputation for missing values.

        Returns:
            Pipeline: scikit-learn preprocessing pipeline
        
        Raises:
            NetworkSecurityException: If pipeline creation fails
        """
        logging.info("Entered get_data_transformer_object method of DataTransformation class")
        try:
            # Initialize KNN Imputer with parameters from config
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"Initialize KNN Imputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}")

            # Create preprocessing pipeline
            processor = Pipeline([
                ("imputer", imputer)
            ])  # type: ignore

            return processor
        except Exception as e:
            raise AutoCareException(e, sys)


    def initiate_data_transformation(self) -> DataTransformationArtifact:  # type: ignore
        """
        Performs the full data transformation process:
        - Reads validated train and test datasets
        - Separates input features and target
        - Applies preprocessing pipeline
        - Saves transformed arrays and pipeline object
        - Returns DataTransformationArtifact with file paths

        Returns:
            DataTransformationArtifact: Artifact containing paths of transformed data and objects
        
        Raises:
            NetworkSecurityException: If any step fails
        """
        logging.info("ENTERED initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting Data Transformation")

            # Load validated train and test datasets
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            # ------------------ Training dataframe ------------------
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)  # Normalize target values

            # ------------------ Testing dataframe ------------------
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            # Get preprocessing pipeline
            preprocessor = self.get_data_transformer_object()

            # Fit pipeline on training features
            preprocessor_object = preprocessor.fit(input_feature_train_df)

            # Transform train and test features
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            # Concatenate transformed features with target for train and test
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # Save transformed numpy arrays
            save_numpy_array_data(self.data_tranformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_tranformation_config.transformed_test_file_path, array=test_arr)

            # Save preprocessing pipeline object
            save_object(self.data_tranformation_config.transformed_object_file_path, preprocessor_object)

            save_object("final_model/preprocessor.pkl", preprocessor_object)
            

            

            # Prepare and return data transformation artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_tranformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_tranformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_tranformation_config.transformed_test_file_path
            )

            return data_transformation_artifact

        except Exception as e:
            raise AutoCareException(e, sys)
