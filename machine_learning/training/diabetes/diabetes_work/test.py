from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging

from machine_learning.training.diabetes.diabetes_work.components.data_ingestion import DataIngestion
from machine_learning.training.diabetes.diabetes_work.entity.config_entity import (
    DataIngestionConfig,
    TrainingPipelineConfig
)


import sys

if __name__ == "__main__":
    try:
        trainingpipelineconfig = TrainingPipelineConfig()

        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)

        logging.info("Initiate the data ingestion")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation Completed")

        print(dataingestionartifact)

    except Exception as e:
        raise AutoCareException(e, sys)
