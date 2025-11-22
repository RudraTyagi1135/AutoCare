# chatbot/core/medical_brain.py
import pickle
from pathlib import Path
import numpy as np
import traceback

# Optional libs
try:
    import shap
except Exception:
    shap = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # AutoCare/
ML_BASE = BASE_DIR / "machine_learning" / "training"

MODEL_PATHS = {
    "diabetes": {
        "model": ML_BASE / "diabetes" / "diabetes_work" / "model_processor" / "model.pkl",
        "preprocessor": ML_BASE / "diabetes" / "diabetes_work" / "model_processor" / "preprocessor.pkl",
    },
    "heart": {
        "model": ML_BASE / "heart" / "heart_work" / "model_processor" / "model.pkl",
        "preprocessor": ML_BASE / "heart" / "heart_work" / "model_processor" / "preprocessor.pkl",
    },
    "stroke": {
        "model": ML_BASE / "stroke" / "stroke_work" / "model_processor" / "model.pkl",
        "preprocessor": ML_BASE / "stroke" / "stroke_work" / "model_processor" / "preprocessor.pkl",
    },
}

_loaded = {}

def _load_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)

def load_model_family(key: str):
    """Load model and preprocessor for `key` (diabetes/heart/stroke). Caches results."""
    if key in _loaded:
        return _loaded[key]
    if key not in MODEL_PATHS:
        raise ValueError("Unknown model key")
    paths = MODEL_PATHS[key]
    model = _load_file(paths["model"])
    preprocessor = _load_file(paths["preprocessor"])
    _loaded[key] = {"model": model, "preprocessor": preprocessor}
    return _loaded[key]

def predict(key: str, raw_features: dict):
    """Accepts a dict of features; returns dict {probability, label, metadata}"""
    try:
        family = load_model_family(key)
        pre = family["preprocessor"]
        model = family["model"]

        # Preprocessor may expect DataFrame; try 1-row transform
        import pandas as pd
        X = pd.DataFrame([raw_features])
        X_proc = pre.transform(X)
        probs = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_proc)[0].tolist()
            positive_index = 1 if len(probs) > 1 else 0
            probability = float(probs[positive_index])
            label = int(model.predict(X_proc)[0])
        else:
            # fallback: model.predict returns score
            score = float(model.predict(X_proc)[0])
            probability = score
            label = 1 if score >= 0.5 else 0

        return {
            "success": True,
            "probability": probability,
            "label": int(label),
            "raw_probs": probs,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}

def explain_shap(key: str, raw_features: dict, nsamples: int = 100):
    """
    Try to compute SHAP values. If shap not available or fails, return a sensible fallback explanation.
    """
    out = {"success": False, "explanation": None}
    try:
        family = load_model_family(key)
        pre = family["preprocessor"]
        model = family["model"]

        # Prepare data
        import pandas as pd
        X = pd.DataFrame([raw_features])
        X_proc = pre.transform(X)

        if shap is None:
            out["explanation"] = "SHAP library not installed. Install `shap` to get interpretability."
            return out

        # Try TreeExplainer first (works for tree ensembles)
        try:
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(X_proc)
        except Exception:
            # Fallback to KernelExplainer (slower)
            background = X_proc if len(X_proc) >= 1 else X_proc
            explainer = shap.KernelExplainer(model.predict_proba, background)
            shap_vals = explainer.shap_values(X_proc, nsamples=nsamples)

        # Convert into human readable list of (feature_name, value, contribution)
        # Attempt to get feature names from preprocessor or X
        feature_names = None
        try:
            # If preprocessor is ColumnTransformer with named transformers, try to fetch final names
            if hasattr(pre, "get_feature_names_out"):
                feature_names = pre.get_feature_names_out()
        except Exception:
            feature_names = None

        # Make a simple mapping
        contributions = []
        if isinstance(shap_vals, list) and len(shap_vals) > 0:
            # shap_vals for class-based => list per class
            sv = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
        else:
            sv = shap_vals

        sv = np.array(sv).reshape(-1)
        if feature_names is None:
            # fallback generic names
            feature_names = [f"f{i}" for i in range(len(sv))]

        for fname, val, contrib in zip(feature_names, X_proc.ravel().tolist()[:len(sv)], sv.tolist()):
            contributions.append({"feature": str(fname), "value": val, "contribution": float(contrib)})

        out["success"] = True
        out["explanation"] = {
            "contributions": contributions,
            "summary_text": "Positive contribution increases predicted risk; negative decreases it."
        }
        return out
    except Exception as e:
        out["explanation"] = f"Failed to compute SHAP: {e}"
        out["trace"] = traceback.format_exc()
        return out
