# machine_learning/prediction/prediction_pipeline.py

import numpy as np
import pandas as pd
from typing import Dict, Any

from machine_learning.prediction.feature_encoder import encode_raw_input
from machine_learning.prediction.load_models import load_model_and_preprocessor
from machine_learning.prediction.utils import prob_to_percent, percent_to_risk_label
from machine_learning.shap_engine.shap_utils import get_shap_details


class Predictor:
    def __init__(self):
        pass

    def _to_python(self, v):
        """Convert numpy types to JSON-safe types."""
        if isinstance(v, (np.integer, np.floating)):
            return v.item()
        if isinstance(v, np.ndarray):
            return v.tolist()
        return v

    def predict(self, disease: str, raw_input: Dict[str, Any]) -> Dict[str, Any]:

        # 1️⃣ Encode raw form input
        full_df = encode_raw_input(raw_input)  # returns 1-row DataFrame

        # 2️⃣ Load model + preprocessor + feature order
        model, preprocessor, feature_columns = load_model_and_preprocessor(disease)

        # 3️⃣ Ensure correct feature alignment
        for col in feature_columns:
            if col not in full_df.columns:
                full_df[col] = np.nan

        df_for_model = full_df[feature_columns].copy()

        # 4️⃣ IMPORTANT FIX — apply preprocessor before prediction
        if preprocessor is not None:
            X_input = preprocessor.transform(df_for_model)
        else:
            X_input = df_for_model.values

        # 5️⃣ Predict probability
        try:
            if hasattr(model, "predict_proba"):
                prob = float(model.predict_proba(X_input)[0][1])
            elif hasattr(model, "decision_function"):
                score = model.decision_function(X_input)[0]
                prob = float(1 / (1 + np.exp(-score)))
            else:
                prob = float(model.predict(X_input)[0])
        except Exception:
            prob = float(model.predict(X_input)[0])

        label = int(prob >= 0.5)

        # 6️⃣ SHAP Explainability
        try:
            explainability = get_shap_details(
                disease=disease,
                pipeline_model=model,
                input_df=df_for_model
            )
        except Exception as shap_error:
            explainability = {
                "error": str(shap_error),
                "message": "SHAP explanation failed."
            }

        # 7️⃣ Final response
        risk_percent = prob_to_percent(prob)

        return {
            "disease": disease,
            "label": self._to_python(label),
            "probability": self._to_python(prob),
            "risk_percent": self._to_python(risk_percent),
            "risk_label": percent_to_risk_label(risk_percent),
            "model": type(model).__name__,
            "used_features": {
                k: self._to_python(v)
                for k, v in df_for_model.iloc[0].to_dict().items()
            },
            "explainability": explainability
        }
