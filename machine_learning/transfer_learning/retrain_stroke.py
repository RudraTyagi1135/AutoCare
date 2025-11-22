import pandas as pd
import pickle
import xgboost as xgb

from machine_learning.ml_utils.main_utils.preprocessing import (
    preprocess_for_diabetes, preprocess_for_heart
)


# Load diabetes + heart models
diab_model = pickle.load(open(".../diabetes/model.pkl", "rb"))
diab_preproc = pickle.load(open(".../diabetes/preprocessor.pkl", "rb"))

heart_model = pickle.load(open(".../heart/model.pkl", "rb"))
heart_preproc = pickle.load(open(".../heart/preprocessor.pkl", "rb"))

df = pd.read_excel("machine_learning/training/stroke/data/Stroke_Final_data.xlsx")

diab_probs = []
heart_probs = []

for idx, row in df.iterrows():

    raw = {...}  # same as before

    dX = preprocess_for_diabetes(raw)
    dXt = diab_preproc.transform(dX)
    diab_p = float(diab_model.predict_proba(dXt)[0][1])
    diab_probs.append(diab_p)

    hX = preprocess_for_heart(raw, diab_p)
    hXt = heart_preproc.transform(hX)
    heart_p = float(heart_model.predict_proba(hXt)[0][1])
    heart_probs.append(heart_p)

df["diabetes"] = diab_probs
df["heart_disease"] = heart_probs


# Train stroke model
y = df["stroke"]
X = df.drop(columns=["stroke"])

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

cat_cols = ["gender"]
preproc = ColumnTransformer([
    ("gender", OneHotEncoder(), cat_cols),
], remainder="passthrough")

model = xgb.XGBClassifier(
    n_estimators=350,
    learning_rate=0.05,
    max_depth=5
)

pipe = Pipeline([
    ("preprocessor", preproc),
    ("model", model)
])

pipe.fit(X, y)

# Save updated stroke model + preprocessor
pickle.dump(pipe, open("machine_learning/training/stroke/stroke_work/model_processor/model.pkl", "wb"))
pickle.dump(preproc, open("machine_learning/training/stroke/stroke_work/model_processor/preprocessor.pkl", "wb"))
