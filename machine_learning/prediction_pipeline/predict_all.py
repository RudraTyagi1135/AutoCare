import pickle
import numpy as np

from machine_learning.ml_utils.main_utils.preprocessing import (
    preprocess_for_diabetes,
    preprocess_for_heart,
    preprocess_for_stroke
)

from rrcf import RCTree


# Load models
diab_model = pickle.load(open(".../diabetes/model.pkl","rb"))
diab_preproc = pickle.load(open(".../diabetes/preprocessor.pkl","rb"))
diab_shap = pickle.load(open("machine_learning/shap_values/diabetes_shap.pkl","rb"))
diab_rrcf = pickle.load(open("machine_learning/RRCF/diabetes_rrcf.pkl","rb"))

heart_model = pickle.load(open(".../heart/model.pkl","rb"))
heart_preproc = pickle.load(open(".../heart/preprocessor.pkl","rb"))
heart_shap = pickle.load(open("machine_learning/shap_values/heart_shap.pkl","rb"))
heart_rrcf = pickle.load(open("machine_learning/RRCF/heart_rrcf.pkl","rb"))

stroke_model = pickle.load(open(".../stroke/model.pkl","rb"))
stroke_preproc = pickle.load(open(".../stroke/preprocessor.pkl","rb"))
stroke_shap = pickle.load(open("machine_learning/shap_values/stroke_shap.pkl","rb"))
stroke_rrcf = pickle.load(open("machine_learning/RRCF/stroke_rrcf.pkl","rb"))


def compute_rrcf_score(forest, point):
    score = 0
    for tree in forest:
        score += tree.codisp(point)
    return score / len(forest)


def predict_all(raw):

    # Diabetes
    dX = preprocess_for_diabetes(raw)
    dXt = diab_preproc.transform(dX)
    diab_prob = float(diab_model.predict_proba(dXt)[0][1])
    diab_shap_vals = diab_shap.shap_values(dXt)
    diab_anomaly = compute_rrcf_score(diab_rrcf, dXt[0])

    # Heart
    hX = preprocess_for_heart(raw, diab_prob)
    hXt = heart_preproc.transform(hX)
    heart_prob = float(heart_model.predict_proba(hXt)[0][1])
    heart_shap_vals = heart_shap.shap_values(hXt)
    heart_anomaly = compute_rrcf_score(heart_rrcf, hXt[0])

    # Stroke
    sX = preprocess_for_stroke(raw, diab_prob, heart_prob)
    sXt = stroke_preproc.transform(sX)
    stroke_prob = float(stroke_model.predict_proba(sXt)[0][1])
    stroke_shap_vals = stroke_shap.shap_values(sXt)
    stroke_anomaly = compute_rrcf_score(stroke_rrcf, sXt[0])

    return {
        "diabetes": {
            "probability": diab_prob,
            "shap": diab_shap_vals.tolist(),
            "anomaly_score": diab_anomaly
        },
        "heart": {
            "probability": heart_prob,
            "shap": heart_shap_vals.tolist(),
            "anomaly_score": heart_anomaly
        },
        "stroke": {
            "probability": stroke_prob,
            "shap": stroke_shap_vals.tolist(),
            "anomaly_score": stroke_anomaly
        }
    }
