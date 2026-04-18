# AutoCare

AutoCare is an AI-assisted healthcare risk assessment system that predicts the likelihood of three conditions:

- Diabetes
- Heart disease
- Stroke

The system combines a web application, rule-based input preparation, trained machine learning models, and SHAP-based explainability to generate prediction results and store user prediction history.

This repository currently reflects the working academic project build used for demonstration and development. It is not yet a finalized MLOps production stack.

## What The System Does

- Accepts manual patient health inputs from the web application
- Encodes raw user inputs into model-ready features
- Runs prediction pipelines for diabetes, heart disease, and stroke
- Produces risk probability, risk percentage, and a simple risk label
- Generates feature-level SHAP explainability for each disease model
- Stores prediction history in MongoDB
- Supports chatbot-based general and medical Q&A in the broader system

## Current Tech Stack

- Backend: Flask
- Machine Learning: scikit-learn, XGBoost
- Explainability: SHAP
- Database: MongoDB
- Frontend: HTML, CSS, JavaScript
- Packaging: setuptools
- Artifact Tracking: DVC was used previously
- Short-term artifact strategy: Git LFS is the practical path for demo builds

## Important Status Note

The codebase includes DVC metadata, but the original S3-backed DVC storage was deleted. Because of that:

- DVC pointer files still exist
- The actual tracked artifact folders are currently missing from this repository snapshot
- For the presentation build, model binaries should be restored or regenerated and then versioned in a simpler way, such as Git LFS

Planned tools such as MLflow, Docker, CI/CD, and a stronger deployment workflow can be added later after the demo milestone.

## System Architecture

At a high level, the project works like this:

1. A user submits health data through the frontend
2. The backend route receives JSON payloads
3. The prediction layer converts raw inputs into disease-specific encoded features
4. Each disease model is loaded with its matching preprocessing object
5. A risk score is generated
6. SHAP explainability is calculated
7. Prediction results are returned to the app and optionally stored in MongoDB history

Core flow:

`manual-entry route -> Predictor -> feature encoding -> model loading -> prediction -> SHAP -> session + MongoDB history`

## Main Project Structure

```text
AutoCare/
├── backend/
│   ├── main.py
│   ├── main2.py
│   ├── app.py
│   ├── update.py
│   └── routes/
│       ├── chatbot_general.py
│       ├── chatbot_medical.py
│       ├── chatbot_summary.py
│       └── manual_entry.py
├── chatbot/
│   ├── core/
│   └── models/
├── frontend/
│   ├── templates/
│   ├── style/
│   │   ├── css/
│   │   └── js/
│   ├── chatbot_general/
│   └── chatbot_medical/
├── machine_learning/
│   ├── prediction/
│   ├── shap_engine/
│   ├── shap_background_data/
│   ├── ml_utils/
│   └── training/
│       ├── diabetes/
│       ├── heart/
│       └── stroke/
├── autocare_utils/
├── requirements.txt
├── setup.py
└── README.MD
```

## Machine Learning Design

The ML subsystem is the core of the health risk engine.

### Supported disease models

- `diabetes`
- `heart`
- `stroke`

### Prediction components

- [machine_learning/prediction/feature_encoder.py](/d:/AutoCare/machine_learning/prediction/feature_encoder.py): converts raw user inputs into numeric features
- [machine_learning/prediction/disease_mapping.py](/d:/AutoCare/machine_learning/prediction/disease_mapping.py): defines model paths and expected feature columns
- [machine_learning/prediction/load_models.py](/d:/AutoCare/machine_learning/prediction/load_models.py): lazily loads model and preprocessing artifacts
- [machine_learning/prediction/prediction_pipeline.py](/d:/AutoCare/machine_learning/prediction/prediction_pipeline.py): runs inference and explainability
- [machine_learning/shap_engine/shap_utils.py](/d:/AutoCare/machine_learning/shap_engine/shap_utils.py): builds disease-level SHAP details

### Input features used by the system

Examples of incoming health indicators:

- gender
- age
- height
- weight
- systolic blood pressure
- diastolic blood pressure
- sleep time
- chest pain
- prior heart attack
- high cholesterol
- walking difficulty
- physical activity
- alcohol use
- smoking
- stress level

These raw inputs are transformed into model features such as:

- `age_category`
- `bmi`
- `obesity`
- `hypertension`
- `stress_category`
- `heart_attack_history`

## Training Pipeline Layout

Each disease has a separate training workspace:

- `machine_learning/training/diabetes/diabetes_work`
- `machine_learning/training/heart/heart_work`
- `machine_learning/training/stroke/stroke_work`

Each workspace follows a similar structure:

- `components/`: ingestion, validation, transformation, training
- `entity/`: config and artifact dataclasses
- `schema/`: dataset schema validation
- `pipeline/`: training pipeline runner
- `model_utils/`: estimator wrappers and metrics
- `logs/`: pipeline logs
- `Artifacts.dvc`: DVC-tracked pipeline outputs
- `model_processor.dvc`: DVC-tracked final serving artifacts

## Backend Integration

The model-serving route in this repository is:

- [backend/routes/manual_entry.py](/d:/AutoCare/backend/routes/manual_entry.py)

This route:

- accepts the patient payload
- normalizes booleans and stress values
- calls the `Predictor` for all three diseases
- stores results in the session
- saves prediction history in MongoDB when configured

## Current Deployment Reality

For the near-term demo build, keep the deployment simple.

Recommended short-term approach:

- restore or retrain the final model artifacts
- store final model binaries with Git LFS
- load models from fixed local paths
- keep MongoDB enabled for history logging
- run the Flask backend locally or on a simple VM/platform

Recommended later approach:

- reintroduce DVC with a valid remote
- add MLflow for experiment tracking
- containerize with Docker
- add CI/CD with GitHub Actions or another pipeline
- formalize AWS deployment

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd AutoCare
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 4. Configure environment variables

Create a `.env` file in the project root with values like:

```env
FLASK_SECRET_KEY=your_secret_key
MONGO_DB_URL=your_mongodb_connection_string
GOOGLE_API_KEY=your_google_gemini_api_key
```

### 5. Ensure model artifacts exist

Before running predictions, make sure the required model and preprocessing files are available locally.

If you are using a demo-safe setup, place the final artifacts in predictable local paths and update the prediction layer accordingly.

### 6. Run the application

```bash
python backend/update.py
```

If you use a different backend entrypoint in your working copy, run that file instead.

## API Overview

### Manual prediction endpoint

`POST /api/manual-entry`

Example request body:

```json
{
  "gender": "Male",
  "age": 45,
  "height": 172,
  "weight": 78,
  "systolic": 135,
  "diastolic": 88,
  "sleeptime": 7,
  "chest_pain": 0,
  "prior_heart_attack": 0,
  "highchol": 1,
  "diffwalk": 0,
  "physactivity": 1,
  "alcohol": 0,
  "smoking": 1,
  "stress_level": 1
}
```

Expected behavior:

- the backend predicts diabetes, heart, and stroke risk
- the results are grouped into a `predictions` object
- the latest result is stored in session
- prediction history is saved to MongoDB when configured

## Explainability

The system uses SHAP to provide feature-level reasoning for model outputs.

Generated explainability includes:

- base value
- SHAP values
- top contributing features

Background samples for SHAP currently live under:

- `machine_learning/shap_background_data/diabetes/background.csv`
- `machine_learning/shap_background_data/heart/background.csv`
- `machine_learning/shap_background_data/stroke/background.csv`

## Limitations

- The repository contains multiple backend entrypoints and overlapping code paths
- The implemented backend is Flask, not FastAPI
- DVC metadata exists, but the original remote-backed artifacts are not currently available
- Some frontend files and scripts are out of sync
- The current repository is closer to a working academic prototype than a cleaned production system

## Recommended Next Steps

For the presentation build:

- finalize a single backend entrypoint
- restore or retrain serving artifacts
- move final model files to Git LFS
- simplify path handling for model loading
- test the end-to-end manual prediction flow

For the post-demo build:

- bring back DVC with a valid remote
- add MLflow tracking
- add Docker support
- add CI/CD
- refactor configuration and deployment structure

## Acknowledgment

AutoCare is being developed as a collaborative academic system. This repository includes work across machine learning, backend, frontend, explainability, and chatbot features.
