# machine_learning/ml_utils/main_utils/preprocessing.py

import numpy as np
import pandas as pd


# -------------------------------------------------------------
# AGE CATEGORY MAPPING
# -------------------------------------------------------------
age_mapping = {
    '0-24': 1, '25-29': 2, '30-34': 3, '35-39': 4, '40-44': 5,
    '45-49': 6, '50-54': 7, '55-59': 8, '60-64': 9, '65-69': 10,
    '70-74': 11, '75-79': 12, '80 or older': 13
}

def convert_age(age_numeric: int):
    if age_numeric <= 24: return 1
    elif age_numeric <= 29: return 2
    elif age_numeric <= 34: return 3
    elif age_numeric <= 39: return 4
    elif age_numeric <= 44: return 5
    elif age_numeric <= 49: return 6
    elif age_numeric <= 54: return 7
    elif age_numeric <= 59: return 8
    elif age_numeric <= 64: return 9
    elif age_numeric <= 69: return 10
    elif age_numeric <= 74: return 11
    elif age_numeric <= 79: return 12
    else: return 13


# -------------------------------------------------------------
# GENERAL CONVERSION UTILITIES
# -------------------------------------------------------------
def yesno(x):
    return 1 if str(x).lower() in ("yes", "true", "1") else 0

def convert_stress(s):
    levels = {
        "no stress": 0,
        "mild": 1,
        "moderate": 2,
        "high": 3,
        "severe": 4
    }
    return levels[str(s).lower()]

def compute_bmi(height_cm, weight_kg):
    h = float(height_cm) / 100
    return round(weight_kg / (h ** 2), 2)

def compute_obesity(bmi):
    return 1 if bmi >= 29 else 0

def compute_hypertension(sys, dia):
    return 1 if sys >= 130 or dia >= 85 else 0


# -------------------------------------------------------------
# PREPROCESS FOR DIABETES MODEL
# -------------------------------------------------------------
def preprocess_for_diabetes(raw):
    height = raw["height_cm"]
    weight = raw["weight_kg"]

    bmi = compute_bmi(height, weight)

    df = pd.DataFrame([{
        "age_category": convert_age(raw["age"]),
        "gender": raw["gender"],
        "bmi": bmi,
        "hypertension": compute_hypertension(raw["systolic"], raw["diastolic"]),
        "smoking": yesno(raw["smoking"]),
        "alcohol": yesno(raw["alcohol"]),
        "highchol": yesno(raw["high_cholesterol"]),
        "diffwalk": yesno(raw["walking_difficulty"]),
        "stress_category": convert_stress(raw["stress_level"]),
        "physactivity": yesno(raw["physical_activity"]),
    }])

    return df


# -------------------------------------------------------------
# PREPROCESS FOR HEART MODEL
# -------------------------------------------------------------
def preprocess_for_heart(raw, diabetes_proba):

    height = raw["height_cm"]
    weight = raw["weight_kg"]
    bmi = compute_bmi(height, weight)

    df = pd.DataFrame([{
        "age_category": convert_age(raw["age"]),
        "gender": raw["gender"],
        "obesity": compute_obesity(bmi),
        "hypertension": compute_hypertension(raw["systolic"], raw["diastolic"]),
        "highchol": yesno(raw["high_cholesterol"]),

        "diabetes": diabetes_proba,

        "heart_attack_history": yesno(raw["prior_heart_attack"]),
        "chest_pain": yesno(raw["chest_pain"]),

        "smoking": yesno(raw["smoking"]),
        "alcohol": yesno(raw["alcohol"]),
        "physactivity": yesno(raw["physical_activity"]),

        "stress_category": convert_stress(raw["stress_level"]),
    }])

    return df


# -------------------------------------------------------------
# PREPROCESS FOR STROKE MODEL
# -------------------------------------------------------------
def preprocess_for_stroke(raw, diabetes_proba, heart_proba):

    height = raw["height_cm"]
    weight = raw["weight_kg"]
    bmi = compute_bmi(height, weight)

    df = pd.DataFrame([{
        "age_category": convert_age(raw["age"]),
        "gender": raw["gender"],
        "bmi": bmi,

        "diabetes": diabetes_proba,
        "heart_disease": heart_proba,

        "smoking": yesno(raw["smoking"]),
        "alcohol": yesno(raw["alcohol"]),
        "physactivity": yesno(raw["physical_activity"]),
        "sleeptime": int(raw["sleep_hours"]),

        "stress_category": convert_stress(raw["stress_level"]),
        "diffwalk": yesno(raw["walking_difficulty"]),
    }])

    return df
