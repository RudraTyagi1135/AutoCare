# 🏥 AutoCare — AI-Powered Healthcare Risk Assessment System

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange)
![SHAP](https://img.shields.io/badge/SHAP-Explainability-red)

## 🔒 Proprietary Project Notice

This repository is publicly visible for portfolio and educational review purposes only.

Unauthorized reuse, reproduction, modification, deployment, redistribution, or commercial usage of this project or its components is strictly prohibited.

**© 2026 Rudra Tyagi. All Rights Reserved.**

---

# 📌 Project Overview

AutoCare is an AI-powered healthcare risk assessment platform that estimates the likelihood of:

- Diabetes
- Heart Disease
- Stroke

The platform combines:

- Machine Learning Inference
- Feature Engineering Pipelines
- SHAP Explainability
- Flask Backend Services
- MongoDB Persistence
- Healthcare Chatbot Integration

to create an end-to-end healthcare intelligence system.

---

# 🎯 Project Objective

The goal of AutoCare is to provide a non-invasive healthcare risk screening system.

```text
Patient Input
      ↓
Feature Engineering
      ↓
Disease-Specific ML Models
      ↓
Risk Prediction
      ↓
SHAP Explainability
      ↓
Prediction History Storage
      ↓
Healthcare Assistance
```

---

# 🧠 Supported Predictions

| Disease | Status |
|----------|----------|
| Diabetes | ✅ |
| Heart Disease | ✅ |
| Stroke | ✅ |

---

# 📊 Prediction Workflow

```text
Frontend Form Submission
            ↓
Flask Backend Route
            ↓
Feature Encoding Layer
            ↓
Disease-Specific ML Models
            ↓
Probability Estimation
            ↓
SHAP Explainability Engine
            ↓
MongoDB Storage
            ↓
Frontend Result Rendering
```

---

# 🏗️ System Architecture

```text
Frontend (HTML/CSS/JS)
            ↓
Flask Backend
            ↓
Prediction Pipeline
            ↓
Feature Engineering
            ↓
Disease Models
            ↓
SHAP Explainability
            ↓
MongoDB Database
```

---

# ⚙️ Architecture Breakdown

## 🖥️ Frontend Layer

### Technologies

- HTML
- CSS
- JavaScript

### Responsibilities

- User Input Collection
- Prediction Rendering
- Chatbot Interaction
- Session Handling

---

## 🌐 Backend Layer

### Technology

- Flask

### Responsibilities

- API Routing
- Request Validation
- Session Handling
- Prediction Orchestration
- MongoDB Integration

---

## 🤖 Machine Learning Layer

### Technologies

- Scikit-Learn
- XGBoost

### Responsibilities

- Model Loading
- Feature Processing
- Risk Prediction
- Probability Estimation

---

## 🧠 Explainability Layer

### Technology

- SHAP

### Responsibilities

- Feature Contribution Analysis
- Prediction Transparency
- Top Risk Factor Identification

Outputs include:

- SHAP Values
- Base Values
- Feature Contributions

---

## 🗄️ Database Layer

### Technology

- MongoDB

### Responsibilities

- Prediction History Storage
- Session Persistence
- Historical Tracking

---

# ✨ Core Features

## 🏥 Multi-Disease Risk Prediction

Supports:

- Diabetes Prediction
- Heart Disease Prediction
- Stroke Prediction

---

## ⚙️ Feature Engineering Pipeline

Transforms raw patient inputs into:

- BMI
- Obesity Indicators
- Hypertension Indicators
- Age Categories
- Stress Categories
- Disease-Specific Encoded Features

---

## 📊 Risk Probability Estimation

Generates:

- Probability Scores
- Risk Percentages
- Risk Labels

---

## 🧠 SHAP Explainability

Provides:

- Feature-Level Explanations
- Model Transparency
- Prediction Interpretability

---

## 💬 Healthcare Chatbots

Includes:

- General Chatbot
- Medical Chatbot
- Prediction Summary Chatbot

---

## 🗄️ Prediction History

Stores:

- User Predictions
- Risk Results
- Historical Sessions

inside MongoDB.

---

# 📂 Project Structure

```text
AutoCare/
│
├── backend/
│   ├── routes/
│   └── update.py
│
├── chatbot/
│   ├── core/
│   └── models/
│
├── frontend/
│   ├── templates/
│   └── style/
│
├── machine_learning/
│   ├── prediction/
│   ├── shap_engine/
│   ├── shap_background_data/
│   ├── ml_utils/
│   └── training/
│
├── autocare_utils/
│
├── requirements.txt
├── setup.py
└── README.md
```

---

# 🧠 Machine Learning Design

## Disease Models

| Model | Status |
|---------|---------|
| Diabetes | ✅ |
| Heart Disease | ✅ |
| Stroke | ✅ |

### Prediction Components

| Component | Responsibility |
|------------|----------------|
| feature_encoder.py | Feature Engineering |
| disease_mapping.py | Path Management |
| load_models.py | Model Loading |
| prediction_pipeline.py | End-to-End Inference |
| shap_utils.py | Explainability |

---

# 📊 Explainability System

AutoCare uses SHAP for prediction transparency.

Generated outputs:

- SHAP Values
- Contribution Scores
- Feature Rankings
- Base Values

Background datasets are stored under:

```text
machine_learning/shap_background_data/
```

---

# ⚙️ Setup Instructions

## 1. Clone Repository

```bash
git clone <repository-url>
cd AutoCare
```

## 2. Create Virtual Environment

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## 4. Configure Environment Variables

Create:

```text
.env
```

Example:

```env
FLASK_SECRET_KEY=your_secret_key
MONGO_DB_URL=your_mongodb_connection_string
GOOGLE_API_KEY=your_google_api_key
```

## 5. Run Application

```bash
python backend/update.py
```

---

# 🚀 Future Roadmap

## Short-Term

- Restore Final Artifacts
- Simplify Model Loading
- Stabilize Backend
- Validate End-to-End Predictions

## Long-Term

- Docker
- MLflow
- FastAPI Migration
- CI/CD
- AWS Deployment
- SageMaker Pipelines
- Monitoring & Logging

---

# 🛠️ Technology Stack

| Layer | Technologies |
|---------|--------------|
| Backend | Flask |
| ML | Scikit-Learn, XGBoost |
| Explainability | SHAP |
| Database | MongoDB |
| Frontend | HTML, CSS, JavaScript |
| Packaging | setuptools |
| Tracking | DVC |

---

# 📸 Screenshots

```markdown
![Dashboard](images/dashboard.png)

![Prediction](images/prediction.png)

![SHAP Analysis](images/shap.png)

![Chatbot](images/chatbot.png)
```

---

# 👨‍💻 Author

**Rudra Tyagi**

### Focus Areas

- ML Systems
- MLOps
- AI Infrastructure
- Explainable AI
- Healthcare AI

---

# ⭐ Recruiter Notes

This project demonstrates:

- End-to-End ML System Design
- Healthcare AI Engineering
- Explainable AI Integration
- Flask Backend Development
- MongoDB Integration
- Multi-Model Inference Architecture
- Production-Oriented ML Thinking

---

# 🔒 License

This repository is proprietary software.

Unauthorized copying, modification, distribution, or commercial use is prohibited.
