# machine_learning/prediction/prediction_pipeline.py

import numpy as np
import pandas as pd
from typing import Dict, Any

from machine_learning.prediction.feature_encoder import encode_raw_input
from machine_learning.prediction.load_models import load_model_and_preprocessor
from machine_learning.prediction.utils import prob_to_percent, percent_to_risk_label


class Predictor:
    def __init__(self):
        """Lightweight prediction orchestrator."""
        pass

    # NOTE: _apply_preprocessor is no longer used for the new ColumnTransformer-based models.
    # We keep it only for possible legacy dict-based preprocessors in future.
    def _apply_preprocessor(self, preprocessor, df_features: pd.DataFrame, feature_columns=None):
        """
        Legacy support if you ever load a dict-style preprocessor.
        Current models DO NOT use this – they rely on the Pipeline in model.pkl.
        """
        if feature_columns is None:
            feature_columns = list(df_features.columns)

        if not isinstance(df_features, pd.DataFrame):
            df_features = pd.DataFrame([df_features], columns=feature_columns)

        df_features = df_features[feature_columns]

        if preprocessor is None:
            return df_features.values

        if hasattr(preprocessor, "transform") and not isinstance(preprocessor, dict):
            return preprocessor.transform(df_features)

        if isinstance(preprocessor, dict):
            arr = df_features[feature_columns].values
            if preprocessor.get("imputer"):
                arr = preprocessor["imputer"].transform(arr)
            if preprocessor.get("scaler"):
                arr = preprocessor["scaler"].transform(arr)
            return arr

        return df_features.values
    
    def _to_python(self, v):
        """Convert numpy values to JSON-safe Python types."""
        if isinstance(v, (np.integer, np.floating)):
            return v.item()
        if isinstance(v, np.ndarray):
            return v.tolist()
        return v


    def predict(self, disease: str, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full structured inference pipeline:

        1. Encode raw manual input → normalized DataFrame (union of all features)
        2. Load (Pipeline model, preprocessor, expected feature_columns) for given disease
        3. Subset + order DataFrame to exactly feature_columns
        4. Feed DataFrame DIRECTLY into model pipeline (which owns its ColumnTransformer)
        5. Return probability, label, and feature snapshot
        """

        # 1️⃣ Encode UI / JSON input into a unified feature frame
        full_df = encode_raw_input(raw_input)  # 1-row DataFrame

        # 2️⃣ Load model pipeline + (unused) preprocessor + expected feature order
        model, preprocessor, feature_columns = load_model_and_preprocessor(disease)

        # 3️⃣ Guarantee all columns exist and in correct order
        for col in feature_columns:
            if col not in full_df.columns:
                full_df[col] = np.nan

        df_for_model = full_df[feature_columns].copy()  # DataFrame, ordered

        # 4️⃣ IMPORTANT: pass DataFrame directly into the model Pipeline
        # The Pipeline already includes ColumnTransformer → it expects a DataFrame with named columns.
        X_input = df_for_model

        # 5️⃣ Predict probability
        try:
            if hasattr(model, "predict_proba"):
                prob = float(model.predict_proba(X_input)[0][1])
            elif hasattr(model, "decision_function"):
                score = model.decision_function(X_input)[0]
                prob = float(1 / (1 + np.exp(-score)))  # sigmoid
            else:
                prob = float(model.predict(X_input)[0])
        except Exception:
            # worst-case fallback
            prob = float(model.predict(X_input)[0])

        label = int(prob >= 0.5)

        # 6️⃣ Build response payload
        return {
        "disease": disease,
        "label": self._to_python(label),
        "probability": self._to_python(prob),
        "risk_percent": self._to_python(prob_to_percent(prob)),
        "risk_label": percent_to_risk_label(prob_to_percent(prob)),
        "model": type(model).__name__,

        # sanitize feature dict
        "used_features": {k: self._to_python(v) for k, v in df_for_model.iloc[0].to_dict().items()},

        # sanitize encoded vector
        "encoded_feature_vector": [self._to_python(v) for v in list(df_for_model.iloc[0].values)],
}

