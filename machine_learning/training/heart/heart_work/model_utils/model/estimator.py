#imports
import os
import sys

from machine_learning.training.heart.heart_work.constant.training_pipeline.constant import SAVED_MODEL_DIR , MODEL_FILE_NAME


from autocare_utils.exception import AutoCareException
from  autocare_utils.logging import logging

class NetworkModel:
    def __init__(self,preprocessor,model):
        try:
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise AutoCareException(e,sys)

    def predict(self,x):
        try:
            x_transform = self.preprocessor.transform(x)
            y_hat = self.model.predict(x_transform)
            return y_hat
        except Exception as e:
            raise AutoCareException(e,sys)
        
                