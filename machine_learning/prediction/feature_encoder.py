# machine_learning/prediction/feature_encoder.py
import numpy as np
import pandas as pd

age_mapping = {
    '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
    '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
    '70-74': 11, '75-79': 12, '80 or older': 13
}

def _age_to_bucket(age_value):
    try:
        a = float(age_value)
    except Exception:
        return np.nan
    if a <= 24: return 1
    if 25 <= a <= 29: return 2
    if 30 <= a <= 34: return 3
    if 35 <= a <= 39: return 4
    if 40 <= a <= 44: return 5
    if 45 <= a <= 49: return 6
    if 50 <= a <= 54: return 7
    if 55 <= a <= 59: return 8
    if 60 <= a <= 64: return 9
    if 65 <= a <= 69: return 10
    if 70 <= a <= 74: return 11
    if 75 <= a <= 79: return 12
    return 13

def _bool_to_int(v):
    if v is None: return 0
    if isinstance(v, (int, float, bool)): return 1 if int(v) == 1 or v is True else 0
    s = str(v).strip().lower()
    return 1 if s in ("1", "yes", "y", "true", "t", "on") else 0

def _map_stress(v):
    if v is None: 
        return np.nan
    s = str(v).strip().lower()

    mapping = {
        "0": 0, "no stress": 0, "none": 0,
        "1": 1, "mild": 1,
        "2": 2, "moderate": 2,
        "3": 3, "high": 3,
        "4": 4, "severe": 4
    }

    return mapping.get(s, np.nan)


def compute_bmi(height_cm, weight_kg):
    try:
        h = float(height_cm)
        w = float(weight_kg)
        if h <= 0: return np.nan
        return round(w / ((h/100.0)**2), 2)
    except Exception:
        return np.nan

def compute_hypertension(systolic, diastolic):
    try:
        s = float(systolic)
        d = float(diastolic)
    except Exception:
        return 0
    return 1 if (s >= 130 or d >= 85) else 0

def encode_raw_input(raw: dict) -> pd.DataFrame:
    """
    Accepts raw dict with keys (user-provided):
    - gender ('Male'/'Female')
    - age (numeric)
    - height (cm)
    - weight (kg)
    - systolic, diastolic
    - sleeptime (hours)
    - chest_pain, prior_heart_attack, diffwalk, physactivity, alcohol, smoking, highchol (booleans)
    - stress_level (text or index)
    Returns a single-row DataFrame with all possible features (union for all models).
    """
    # default None fetch
    def g(k): return raw.get(k, None)

    gender_raw = g("gender")
    gender = 1 if str(gender_raw).strip().lower() in ["male", "m"] else 0

    age_bucket = _age_to_bucket(g("age"))

    height = g("height")
    weight = g("weight")
    bmi = compute_bmi(height, weight)

    systolic = g("systolic")
    diastolic = g("diastolic")
    hypertension = compute_hypertension(systolic, diastolic)

    sleeptime = None
    try:
        sleeptime = int(g("sleeptime")) if g("sleeptime") is not None else np.nan   #ignore float sleeptime
    except Exception:
        sleeptime = np.nan

    chest_pain = _bool_to_int(g("chest_pain"))
    prior_heart_attack = _bool_to_int(g("prior_heart_attack"))
    diffwalk = _bool_to_int(g("diffwalk"))
    physactivity = _bool_to_int(g("physactivity"))
    alcohol = _bool_to_int(g("alcohol"))
    smoking = _bool_to_int(g("smoking"))
    highchol = _bool_to_int(g("highchol"))
    stress_category = _map_stress(g("stress_level"))

    # obesity for heart model (binarize from bmi)
    obesity = None
    try:
        obesity = 1 if float(bmi) > 29 else 0
    except Exception:
        obesity = 0

    row = {
    "age_category": age_bucket,
    "gender": gender,
    "bmi": bmi,
    "obesity": obesity,
    "hypertension": hypertension,
    "sleeptime": sleeptime,  # unified name
    "chest_pain": chest_pain,
    "heart_attack_history": prior_heart_attack,  # single authoritative name
    "diffwalk": diffwalk,
    "physactivity": physactivity,
    "alcohol": alcohol,
    "smoking": smoking,
    "highchol": highchol,
    "stress_category": stress_category
}


    df = pd.DataFrame([row])
    return df
