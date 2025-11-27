# machine_learning/prediction/load_models.py
import os
import logging
from typing import Tuple, Any, Optional
from machine_learning.prediction.disease_mapping import DISEASE_MAP
from machine_learning.ml_utils.main_utils.utils import load_object
import joblib

logger = logging.getLogger(__name__)

def _exists(path):
    return path is not None and os.path.exists(str(path))

def load_model_and_preprocessor(disease: str) -> Tuple[Any, Any, list]:
    """
    Returns: (model, preprocessor, feature_columns)
    - preprocessor may be:
        - sklearn transformer (has .transform)
        - dict with keys: {'imputer','scaler','feature_columns'}
    """
    if disease not in DISEASE_MAP:
        raise ValueError(f"Unknown disease '{disease}'")

    cfg = DISEASE_MAP[disease]
    print("\n🔍 DEBUG PATH CHECK")
    print(f" Looking for: {cfg['model_path']}")
    print(f" Exists: {os.path.exists(cfg['model_path'])}")
    print("---------------")

    model_path = cfg["model_path"]
    preproc_path = cfg["preprocessor_path"]
    features = cfg["features"]

    model = None
    preprocessor = None

    # try load model
    if _exists(model_path):
        try:
            model = load_object(str(model_path))
        except Exception:
            # fallback to joblib
            model = joblib.load(str(model_path))
    else:
        raise FileNotFoundError(f"Model not found: {model_path}")

    if _exists(preproc_path):
        try:
            preprocessor = load_object(str(preproc_path))
        except Exception:
            try:
                preprocessor = joblib.load(str(preproc_path))
            except Exception as e:
                logger.warning(f"Could not load preprocessor pickle: {e}")
                preprocessor = None
    else:
        logger.warning(f"Preprocessor file not found at: {preproc_path}. The model may require raw arrays.")
        preprocessor = None

    # if preprocessor is dict and has feature_columns, expose them
    feature_columns = features
    if isinstance(preprocessor, dict):
        feature_columns = preprocessor.get("feature_columns", features)

    return model, preprocessor, feature_columns
