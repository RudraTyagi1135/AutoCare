import pandas as pd
import pickle
import xgboost as xgb

from machine_learning.ml_utils.main_utils.preprocessing import preprocess_for_diabetes


# ------------------------------------------------------------
# Load diabetes model + preprocessor
# ------------------------------------------------------------
diab_model = pickle.load(open("machine_learning/training/diabetes/diabetes_work/model_processor/model.pkl", "rb"))
diab_preproc = pickle.load(open("machine_learning/training/diabetes/diabetes_work/model_processor/preprocessor.pkl", "rb"))

# ------------------------------------------------------------
# Load heart dataset
# ------------------------------------------------------------
df = pd.read_excel("machine_learning/training/heart/data/Heart_Final_data.xlsx")

# ------------------------------------------------------------
# STEP 1 — Generate diabetes_proba
# ------------------------------------------------------------
diab_features = []

for idx, row in df.iterrows():
    raw = {
        "gender": row["gender"],
        "age": row["age_numeric"],
        "height_cm": row["height"],
        "weight_kg": row["weight"],
        "systolic": row["systolic"],
        "diastolic": row["diastolic"],
        "smoking": row["smoking"],
        "alcohol": row["alcohol"],
        "high_cholesterol": row["highchol"],
        "walking_difficulty": row["diffwalk"],
        "stress_level": row["stress_category"],
        "physical_activity": row["physactivity"],
        "sleep_hours": row["sleeptime"],
        "chest_pain": row["chest_pain"],
        "prior_heart_attack": row["heart_attack_history"],
    }

    df_d = preprocess_for_diabetes(raw)
    Xt = diab_preproc.transform(df_d)
    proba = float(diab_model.predict_proba(Xt)[0][1])
    diab_features.append(proba)

df["diabetes_proba"] = diab_features

# Replace old diabetes column
df["diabetes"] = df["diabetes_proba"]


# ------------------------------------------------------------
# Train updated heart model
# ------------------------------------------------------------
y = df["heart_disease"]
X = df.drop(columns=["heart_disease", "diabetes_proba"])

# Load heart preprocessing pipeline from schema
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

cat_cols = ["gender"]
preproc = ColumnTransformer([
    ("gender", OneHotEncoder(), cat_cols),
], remainder="passthrough")

model = xgb.XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5
)

pipe = Pipeline([
    ("preprocessor", preproc),
    ("model", model)
])

pipe.fit(X, y)

# Save new heart model
pickle.dump(pipe, open("machine_learning/training/heart/heart_work/model_processor/model.pkl", "wb"))
pickle.dump(preproc, open("machine_learning/training/heart/heart_work/model_processor/preprocessor.pkl", "wb"))
