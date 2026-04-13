# machine_learning/prediction/load_models.py

import os
import logging
from typing import Tuple, Any
from machine_learning.prediction.disease_mapping import DISEASE_MAP
from machine_learning.ml_utils.main_utils.utils import load_object
import joblib

logger = logging.getLogger(__name__)

# ✅ Cache to store loaded models (Lazy Loading)
_MODEL_CACHE = {}


def _exists(path):
    return path is not None and os.path.exists(str(path))


def load_model_and_preprocessor(disease: str) -> Tuple[Any, Any, list]:
    """
    Returns: (model, preprocessor, feature_columns)

    - preprocessor may be:
        - sklearn transformer (has .transform)
        - dict with keys: {'imputer','scaler','feature_columns'}
    """

    # ✅ Step 1: Check cache first (Lazy Loading)
    if disease in _MODEL_CACHE:
        logger.info(f"Using cached model for {disease}")
        return _MODEL_CACHE[disease]

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

    # ✅ Load model
    if _exists(model_path):
        try:
            model = load_object(str(model_path))
        except Exception:
            model = joblib.load(str(model_path))
    else:
        raise FileNotFoundError(f"Model not found: {model_path}")

    # ✅ Load preprocessor
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
        logger.warning(
            f"Preprocessor file not found at: {preproc_path}. The model may require raw arrays."
        )
        preprocessor = None

    # ✅ Feature columns handling
    feature_columns = features
    if isinstance(preprocessor, dict):
        feature_columns = preprocessor.get("feature_columns", features)

    # ✅ Step 2: Store in cache
    _MODEL_CACHE[disease] = (model, preprocessor, feature_columns)

    return _MODEL_CACHE[disease]