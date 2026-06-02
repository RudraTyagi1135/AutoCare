#macine_learning/ml_utils/main_utils/utils.py
import yaml
import os
import sys
from autocare_utils.exception import AutoCareException
from autocare_utils.logging import logging
import numpy as np
import dill
import pickle
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV

def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its content as a Python dictionary.

    Args:
        file_path (str): Path to the YAML file to read.

    Returns:
        dict: Parsed content of the YAML file.

    Raises:
        NetworkSecurityException: If reading or parsing the file fails.
    """
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise AutoCareException(e, sys)


def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """
    Writes Python object content into a YAML file.

    Args:
        file_path (str): Path where the YAML file should be written.
        content (object): Python object to serialize into YAML.
        replace (bool): If True and file exists, removes it before writing.

    Raises:
        NetworkSecurityException: If writing the YAML file fails.
    """
    try:
        # Remove existing file if replace is True
        if replace and os.path.exists(file_path):
            os.remove(file_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write content to YAML
        with open(file_path, "w") as file:
            yaml.dump(content, file)
            
    except Exception as e:
        raise AutoCareException(e, sys)
    

def save_numpy_array_data(file_path: str , array:np.array): #type: ignore

    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)

        with open(file_path , "wb") as file_obj:
            np.save(file_obj , array)

    except Exception as e:
        raise AutoCareException(e,sys) from e     
     

def load_numpy_array_data(file_path: str) -> np.array:  #type:ignore
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise AutoCareException(e, sys)




def save_object(file_path: str , obj:object) -> None:
    try:
        logging.info("Entered the save object method of MainUtils class")

        os.makedirs(os.path.dirname(file_path) , exist_ok=True) 

        with open(file_path , "wb") as file_obj:
            pickle.dump(obj, file_obj)

        logging.info("exited the save object method of MainUtils class")
    except Exception as e:
        raise AutoCareException(e,sys)     


def load_object(file_path: str, ) -> object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} is not exists")
        
        with open(file_path, "rb") as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
        
    except Exception as e:
        raise AutoCareException(e, sys) from e      



# def evaluate_models(X_train, y_train,X_test,y_test,models,param):
#     try:
#         report = {}

#         for i in range(len(list(models))):
#             model = list(models.values())[i]
#             para=param[list(models.keys())[i]]

#             gs = GridSearchCV(model,para,cv=3)
#             gs.fit(X_train,y_train)

#             model.set_params(**gs.best_params_)
#             model.fit(X_train,y_train)

#             #model.fit(X_train, y_train)  # Train model

#             y_train_pred = model.predict(X_train)

#             y_test_pred = model.predict(X_test)

#             train_model_score = r2_score(y_train, y_train_pred)

#             test_model_score = r2_score(y_test, y_test_pred)

#             report[list(models.keys())[i]] = test_model_score

#         return report

#     except Exception as e:
#         raise AutoCareException(e, sys)