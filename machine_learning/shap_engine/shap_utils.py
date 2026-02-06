import shap
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[2] / "machine_learning"
BACKGROUND_CACHE = {}
EXPLAINER_CACHE = {}


def _coerce_background_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure background DataFrame is numeric where the model expects numeric.
    Fixes errors like: 'could not convert string to float: Female'.
    """
    df = df.copy()

    # gender: 'Male' / 'Female' -> 1 / 0
    if "gender" in df.columns and df["gender"].dtype == object:
        df["gender"] = df["gender"].map({"Male": 1, "Female": 0}).astype(float)

    # If you later discover any other string-coded numeric fields,
    # add mappings here (for example Yes/No, True/False, etc.)

    return df


def load_background(disease: str) -> pd.DataFrame:
    """
    Loads the pre-generated background dataset.
    Cached after first load for performance.
    """
    if disease in BACKGROUND_CACHE:
        return BACKGROUND_CACHE[disease]

    # file_path = ROOT / "shap_values" / disease / "background.csv"
    file_path = ROOT / "shap_background_data" / disease / "background.csv"


    if not file_path.exists():
        raise FileNotFoundError(
            f"SHAP background.csv missing for {disease} — run background_builder.py first."
        )

    df = pd.read_csv(file_path)
    df = _coerce_background_numeric(df)
    BACKGROUND_CACHE[disease] = df
    return df


def select_explainer(model, background):
    """Auto-select best SHAP explainer based on algorithm type."""
    if isinstance(model, (RandomForestClassifier, GradientBoostingClassifier)):
        return shap.TreeExplainer(model, background)

    if isinstance(model, LogisticRegression):
        return shap.LinearExplainer(model, background)

    # Fallback for any other estimator
    return shap.Explainer(model, background)


def _normalize_shap_arrays(explanation):
    """
    Normalize SHAP explanation values & base_values into 1D numeric arrays/scalars,
    robust against different SHAP backends (Tree, Linear, model-agnostic).
    """
    # ---- values ----
    values = np.array(explanation.values)

    if values.ndim == 3:
        # e.g. (n_outputs, n_samples, n_features)
        # assume binary/single-output -> take first output & first sample
        values = values[0, 0, :]
    elif values.ndim == 2:
        # e.g. (n_samples, n_features)
        values = values[0, :]
    elif values.ndim == 1:
        # e.g. (n_features,)
        values = values
    else:
        # unexpected -> flatten
        values = values.reshape(-1)

    # ---- base_values ----
    base = np.array(explanation.base_values)
    if base.ndim > 0:
        base_scalar = float(base.reshape(-1)[0])
    else:
        base_scalar = float(base)

    return values.astype(float), base_scalar

def get_shap_details(disease: str, pipeline_model, input_df: pd.DataFrame):
    """
    Generates SHAP contribution metrics.
    Works for:
    - sklearn Pipeline models
    - Plain tree/linear estimators
    """

    try:
        # -----------------------------
        # CASE 1: Model is sklearn Pipeline
        # -----------------------------
        if hasattr(pipeline_model, "named_steps"):

            transformer = pipeline_model.named_steps.get("preprocessor")
            model = pipeline_model.named_steps.get("model")

            bg_raw = load_background(disease)

            if transformer is not None:
                X_background = transformer.transform(bg_raw)
                X_input = transformer.transform(input_df)
            else:
                X_background = bg_raw.values
                X_input = input_df.values

        # -----------------------------
        # CASE 2: Plain trained model
        # -----------------------------
        else:
            model = pipeline_model
            bg_raw = load_background(disease)
            X_background = bg_raw.values
            X_input = input_df.values

        # -----------------------------
        # Build SHAP explainer
        # -----------------------------
        explainer = EXPLAINER_CACHE.get(disease)
        if explainer is None:
            explainer = select_explainer(model, X_background)
            EXPLAINER_CACHE[disease] = explainer

        explanation = explainer(X_input)

        values, base_value = _normalize_shap_arrays(explanation)

        feature_names = list(input_df.columns)
        sorted_idx = np.argsort(np.abs(values))[::-1]

        return {
            "base_value": float(base_value),
            "feature_names": feature_names,
            "shap_values": values.tolist(),
            "top_contributors": [
                {"feature": feature_names[i], "impact": float(values[i])}
                for i in sorted_idx[:5]
            ],
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "SHAP explanation failed. Background or model mismatch."
        }
