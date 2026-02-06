# machine_learning/prediction/disease_mapping.py

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2] / "machine_learning"


def get_latest_artifact_path(base_path: Path) -> Path:
    artifacts_dir = base_path / "Artifacts"
    if not artifacts_dir.exists():
        raise FileNotFoundError(f"No Artifacts folder found at {artifacts_dir}")

    folders = [f for f in artifacts_dir.iterdir() if f.is_dir()]
    if not folders:
        raise FileNotFoundError(f"No artifact runs found inside {artifacts_dir}")

    latest_folder = sorted(folders)[-1]
    return latest_folder


def build_paths(disease_name: str, work_folder: str):
    base = ROOT / "training" / disease_name / work_folder
    latest = get_latest_artifact_path(base)

    return {
        "model_path": latest / "model_trainer" / "trained_model" / "model.pkl",
        "preprocessor_path": latest / "data_transformation" / "transformed_object" / "preprocessing.pkl",
    }


DISEASE_MAP = {
    "diabetes": {
        **build_paths("diabetes", "diabetes_work"),
        "features": [
            "age_category", "gender", "bmi", "hypertension", "smoking",
            "alcohol", "highchol", "diffwalk", "stress_category", "physactivity"
        ],
    },

    "heart": {
        **build_paths("heart", "heart_work"),
        "features": [
            "age_category", "gender", "obesity", "hypertension", "highchol",
            "heart_attack_history", "chest_pain", "smoking", "alcohol",
            "physactivity", "stress_category"
        ],
    },

    "stroke": {
        **build_paths("stroke", "stroke_work"),
        "features": [
            "age_category", "gender", "bmi", "smoking", "alcohol",
            "physactivity", "sleeptime", "stress_category", "diffwalk"
        ],
    },
}
