import shap
import pickle
import numpy as np

MODELS = [
    ("diabetes", "machine_learning/training/diabetes/diabetes_work/model_processor"),
    ("heart", "machine_learning/training/heart/heart_work/model_processor"),
    ("stroke", "machine_learning/training/stroke/stroke_work/model_processor"),
]

for name, path in MODELS:
    model = pickle.load(open(f"{path}/model.pkl", "rb"))
    preproc = pickle.load(open(f"{path}/preprocessor.pkl", "rb"))
    train = np.load(f"{path.replace('model_processor','data_transformation/transformed')}/train.npy")

    explainer = shap.TreeExplainer(model.named_steps["model"])
    pickle.dump(
        explainer,
        open(f"machine_learning/shap_values/{name}_shap.pkl", "wb")
    )
