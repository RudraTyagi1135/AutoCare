import pandas as pd
from pathlib import Path
from machine_learning.prediction.disease_mapping import DISEASE_MAP

ROOT = Path(__file__).resolve().parents[2] / "machine_learning"


def get_latest_validated_train(disease: str) -> Path:
    """
    Automatically finds the latest timestamp folder path:
    machine_learning/training/<disease>/<disease>_work/Artifacts/<TIMESTAMP>/data_validation/validated/train.csv
    """
    base_dir = ROOT / "training" / disease / f"{disease}_work" / "Artifacts"

    if not base_dir.exists():
        raise FileNotFoundError(f"Artifacts folder not found for {disease}")

    # Find all timestamp folders (sorted newest → oldest)
    timestamp_dirs = sorted(
        [p for p in base_dir.iterdir() if p.is_dir()],
        reverse=True
    )

    for folder in timestamp_dirs:
        train_path = folder / "data_validation" / "validated" / "train.csv"
        if train_path.exists():
            return train_path

    raise FileNotFoundError(f"No validated training data found for disease: {disease}")


def build_background(disease: str):
    """Creates SHAP background from the validated training dataset."""
    print(f"\n📌 Building SHAP background for: {disease}")

    train_file = get_latest_validated_train(disease)
    df = pd.read_csv(train_file)

    # Select only columns required for this disease (encoded feature space)
    feature_cols = DISEASE_MAP[disease]["features"]
    df = df[feature_cols]

    # Sample 50 rows for SHAP baseline
    if len(df) > 50:
        df_sample = df.sample(50, random_state=42)
    else:
        df_sample = df.copy()

    # Save background
    save_dir = ROOT / "shap_values" / disease
    save_dir.mkdir(parents=True, exist_ok=True)

    out_path = save_dir / "background.csv"
    df_sample.to_csv(out_path, index=False)

    print(f"✔ Saved background for {disease}: {out_path}")


if __name__ == "__main__":
    for disease in DISEASE_MAP.keys():
        try:
            build_background(disease)
        except Exception as e:
            print(f"❌ Failed for {disease}: {e}")
        else:
            print(f"🎉 SHAP background ready for {disease}")
