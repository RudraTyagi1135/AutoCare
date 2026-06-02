# machine_learning/ml_utils/main_utils/preprocessing.py
import numpy as np
import pandas as pd

age_mapping = {
    '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
    '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
    '70-74': 11, '75-79': 12, '80 or older': 13
}

stress_map = {"no stress":0, "mild":1, "moderate":2, "high":3, "severe":4}

def to_bool_int(value):
    return 1 if str(value).strip().lower() in ("1","yes","y","true","t") else 0

def gender_to_int(g):
    return 1 if str(g).strip().lower() in ("male","m") else 0

def age_to_category(age):
    # numeric age to bucket (use your mapping). Example thresholds:
    age = int(age)
    if age <= 24: return 1
    if 25 <= age <= 29: return 2
    if 30 <= age <= 34: return 3
    if 35 <= age <= 39: return 4
    if 40 <= age <= 44: return 5
    if 45 <= age <= 49: return 6
    if 50 <= age <= 54: return 7
    if 55 <= age <= 59: return 8
    if 60 <= age <= 64: return 9
    if 65 <= age <= 69: return 10
    if 70 <= age <= 74: return 11
    if 75 <= age <= 79: return 12
    return 13

def compute_bmi(height_cm, weight_kg):
    if height_cm and weight_kg:
        return weight_kg / ((height_cm/100)**2)
    return np.nan

def hypertension_from_bp(systolic, diastolic):
    try:
        s = float(systolic); d = float(diastolic)
        return 1 if (s >= 130 or d >= 85) else 0
    except:
        return 0

def infer_obesity_from_bmi(bmi):
    return 1 if bmi > 29 else 0

def map_stress(s):
    return stress_map.get(str(s).strip().lower(), 0)



def preprocess_user_inputs(raw):
    # raw: dict with keys matching your UI
    bmi = compute_bmi(raw.get("height_cm"), raw.get("weight_kg"))
    age_cat = age_to_category(raw.get("age"))
    gender = gender_to_int(raw.get("gender"))
    hypert = hypertension_from_bp(raw.get("systolic"), raw.get("diastolic"))
    smoking = to_bool_int(raw.get("smoking"))
    alcohol = to_bool_int(raw.get("alcohol"))
    phys = to_bool_int(raw.get("physactivity"))
    diffwalk = to_bool_int(raw.get("diffwalk"))
    highchol = to_bool_int(raw.get("highchol"))
    chest_pain = to_bool_int(raw.get("chest_pain"))
    prior_mi = to_bool_int(raw.get("prior_heart_attack"))
    sleeptime = int(raw.get("sleeptime") or 0)
    stress = map_stress(raw.get("stress_level"))

    df_diab = pd.DataFrame([[
        age_cat, gender, bmi, hypert, smoking, alcohol, highchol, diffwalk, stress, phys
    ]], columns=[
        "age_category","gender","bmi","hypertension","smoking","alcohol","highchol","diffwalk","stress_category","physactivity"
    ])

    df_heart = pd.DataFrame([[
        age_cat, gender, infer_obesity_from_bmi(bmi), hypert, highchol, prior_mi, chest_pain, smoking, alcohol, phys, stress
    ]], columns=[
        "age_category","gender","obesity","hypertension","highchol","heart_attack_history","chest_pain","smoking","alcohol","physactivity","stress_category"
    ])

    df_stroke = pd.DataFrame([[
        age_cat, gender, bmi, smoking, alcohol, phys, sleeptime, stress, diffwalk
    ]], columns=[
        "age_category","gender","bmi","smoking","alcohol","physactivity","sleeptime","stress_category","diffwalk"
    ])

    return df_diab, df_heart, df_stroke
