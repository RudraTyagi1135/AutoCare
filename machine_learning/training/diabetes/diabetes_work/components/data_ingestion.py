# ============================ #
#   Data Ingestion Component   #
# ============================ #

# -------- Standard Imports --------
import os
import sys
import pymongo
import numpy as np
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split

# -------- Internal Imports --------
from autocare_utils.exception import AutoCareException  # Custom exception handling
from autocare_utils.logging import logging                        # Project-level logging

# -------- Environment Variables Loader --------
from dotenv import load_dotenv   # dotenv helps load secrets (like MongoDB credentials) from .env file
load_dotenv()

# Load MongoDB URL from environment (never hardcode in codebase for security)
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)  # Debugging ONLY → remove later in production for security reasons

# -------- Config / Entity Imports --------
from machine_learning.training.diabetes.diabetes_work.entity.config_entity import DataIngestionConfig
     # Holds ingestion-related configs
from machine_learning.training.diabetes.diabetes_work.entity.artifact_entity import DataIngestionArtifact # Holds ingestion output metadata



# ============================================================ #
#                 Data Ingestion Class                         #
# ============================================================ #
class DataIngestion:
    """
    Handles the full lifecycle of data ingestion:
    1. Export data from MongoDB into a DataFrame.
    2. Store raw data into a feature store (CSV).
    3. Split data into training & testing sets.
    4. Return DataIngestionArtifact with file paths.
    """

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        """
        Constructor initializes DataIngestion with config entity.
        Args:
            data_ingestion_config (DataIngestionConfig): Configuration object
        """
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise AutoCareException(e, sys)


    # ---------------- Export from MongoDB ----------------
    def export_collection_as_dataframe(self):
        """
        Fetch data from MongoDB collection and return as DataFrame.
        Steps:
        - Connect to MongoDB using env URL.
        - Convert collection to Pandas DataFrame.
        - Drop _id field (not needed for ML pipeline).
        - Replace placeholder "na" with np.nan.
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            # Connect to MongoDB
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]

            # Fetch collection as DataFrame
            df = pd.DataFrame(list(collection.find()))

            # Drop MongoDB internal ID column (not useful for ML)
            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], axis=1, inplace=True)

            print("Rows fetched from MongoDB:", df.shape[0])  # Debugging check

            # Replace string "na" with np.nan for missing values
            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise AutoCareException(e, sys)


    # ---------------- Save Raw Data to Feature Store ----------------
    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        """
        Save the entire dataset into a feature store (CSV file).
        Purpose:
        - Keeps a raw copy of ingested data before train-test split.
        """
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path

            # Ensure directory exists
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            # Save DataFrame to CSV
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe

        except Exception as e:
            raise AutoCareException(e, sys)


    # ---------------- Train-Test Split ----------------
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        """
        Split dataset into training & testing sets.
        Saves the split files to configured paths.
        """
        try:
            # Perform split
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train-test split on dataset")

            # Ensure directory exists for saving train/test files
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info("Exporting train-test split files")

            # Save training set
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            # Save testing set
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )

            logging.info("Exported train-test split files successfully")

        except Exception as e:
            raise AutoCareException(e, sys)


    # ---------------- Orchestrator ----------------
    def initiate_data_ingestion(self):
        """
        Main method to orchestrate ingestion process:
        1. Pull data from MongoDB.
        2. Save raw dataset to feature store.
        3. Perform train-test split.
        4. Return DataIngestionArtifact with file paths.
        """
        try:
            # Step 1: Fetch data
            dataframe = self.export_collection_as_dataframe()

            # Step 2: Save into feature store
            dataframe = self.export_data_into_feature_store(dataframe)

            # Step 3: Split into train/test
            self.split_data_as_train_test(dataframe)

            # Step 4: Create artifact (output metadata)
            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            return data_ingestion_artifact

        except Exception as e:
            raise AutoCareException(e, sys)
