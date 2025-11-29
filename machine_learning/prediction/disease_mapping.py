# machine_learning/prediction/disease_mapping.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "machine_learning"


DISEASE_MAP = {
    "diabetes": {
        "model_path": ROOT / "training" / "diabetes" / "diabetes_work" / "model_processor" / "model.pkl",
        "preprocessor_path": ROOT / "training" / "diabetes" / "diabetes_work" / "model_processor" / "preprocessor.pkl",
        "features": [
            "age_category", "gender", "bmi", "hypertension", "smoking",
            "alcohol", "highchol", "diffwalk", "stress_category", "physactivity"
        ],
    },
    "heart": {
        "model_path": ROOT / "training" / "heart" / "heart_work" / "model_processor" / "model.pkl",
        "preprocessor_path": ROOT / "training" / "heart" / "heart_work" / "model_processor" / "preprocessor.pkl",
        "features": [
            "age_category", "gender", "obesity", "hypertension", "highchol",
            "heart_attack_history", "chest_pain", "smoking", "alcohol", "physactivity", "stress_category"
        ],
    },
    "stroke": {
        "model_path": ROOT / "training" / "stroke" / "stroke_work" / "model_processor" / "model.pkl",
        "preprocessor_path": ROOT / "training" / "stroke" / "stroke_work" / "model_processor" / "preprocessor.pkl",
        "features": [
            "age_category", "gender", "bmi", "smoking", "alcohol",
            "physactivity", "sleeptime", "stress_category", "diffwalk"
        ],
    },
}
