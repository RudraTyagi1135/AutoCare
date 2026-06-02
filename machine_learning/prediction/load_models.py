# machine_learning/prediction/load_models.py

import os
import logging
from typing import Tuple, Any

import joblib

from machine_learning.prediction.disease_mapping import DISEASE_MAP
from machine_learning.ml_utils.main_utils.utils import load_object

logger = logging.getLogger(__name__)

# ==========================================
# MODEL CACHE (Lazy Loading)
# ==========================================
_MODEL_CACHE = {}


def _exists(path):
    return path is not None and os.path.exists(str(path))


def load_model_and_preprocessor(disease: str) -> Tuple[Any, Any, list]:
    """
    Returns:
        model,
        preprocessor,
        feature_columns

    Preprocessor may be:
        1. sklearn transformer
        2. dict containing:
           {
               "imputer",
               "scaler",
               "feature_columns"
           }
    """

    # ==========================================
    # CACHE CHECK
    # ==========================================
    if disease in _MODEL_CACHE:
        logger.info(f"Using cached model for {disease}")
        return _MODEL_CACHE[disease]

    # ==========================================
    # VALIDATE DISEASE
    # ==========================================
    if disease not in DISEASE_MAP:
        raise ValueError(f"Unknown disease '{disease}'")

    cfg = DISEASE_MAP[disease]

    model_path = cfg["model_path"]
    preproc_path = cfg["preprocessor_path"]
    feature_columns = cfg["features"]

    logger.info(f"Loading model for disease: {disease}")

    # ==========================================
    # LOAD MODEL
    # ==========================================
    if not _exists(model_path):
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    try:
        model = load_object(str(model_path))
    except Exception:
        model = joblib.load(str(model_path))

    # ==========================================
    # LOAD PREPROCESSOR
    # ==========================================
    preprocessor = None

    if _exists(preproc_path):
        try:
            preprocessor = load_object(str(preproc_path))

        except Exception:
            try:
                preprocessor = joblib.load(str(preproc_path))

            except Exception as e:
                logger.warning(
                    f"Could not load preprocessor: {e}"
                )
                preprocessor = None

    else:
        logger.warning(
            f"Preprocessor not found: {preproc_path}"
        )

    # ==========================================
    # FEATURE COLUMNS
    # ==========================================
    if isinstance(preprocessor, dict):
        feature_columns = preprocessor.get(
            "feature_columns",
            feature_columns
        )

    # ==========================================
    # CACHE MODEL
    # ==========================================
    _MODEL_CACHE[disease] = (
        model,
        preprocessor,
        feature_columns
    )

    logger.info(
        f"Successfully loaded model for {disease}"
    )

    return _MODEL_CACHE[disease]