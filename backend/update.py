# ==========================================
# AutoCare - FINAL STABLE VERSION
# ==========================================

import os
import sys
from pathlib import Path
from datetime import datetime
from functools import wraps
from io import BytesIO
from datetime import timedelta

# ------------------------------------------
# FIX PROJECT ROOT IMPORT ISSUE
# ------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# ------------------------------------------
# FLASK IMPORTS
# ------------------------------------------
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    make_response
)

from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_cors import CORS

# ------------------------------------------
# PDF (ReportLab — No GTK needed)
# ------------------------------------------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


# ==========================================
# PATH CONFIG
# ==========================================
TEMPLATES_DIR = ROOT / "frontend" / "templates"
STATIC_DIR = ROOT / "frontend" / "style"

print("🚀 AutoCare Backend Running")
print("Templates:", TEMPLATES_DIR)
print("Static:", STATIC_DIR)

# ==========================================
# LOAD ENV
# ==========================================
load_dotenv(ROOT / ".env")

# ==========================================
# APP INIT
# ==========================================
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path="/style"
)

CORS(app)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise Exception("Missing FLASK_SECRET_KEY in .env")

# ==========================================
# DATABASE
# ==========================================
MONGO_URI = os.getenv("MONGO_DB_URL")
if not MONGO_URI:
    raise Exception("Missing MONGO_DB_URL in .env")

client = MongoClient(MONGO_URI)
db = client["History"]
users_col = db["users"]
app.config["DB"] = db
history_col = db["prediction_history"]
app.config["users_col"] = users_col
app.config["history_col"] = history_col


# ==========================================
# REGISTER BLUEPRINTS (DO NOT REMOVE)
# ==========================================
from routes.chatbot_general import general_chat_bp
from routes.chatbot_medical import medical_bp
from routes.manual_entry import manual_bp

app.register_blueprint(general_chat_bp, url_prefix="/api")
app.register_blueprint(medical_bp)
app.register_blueprint(manual_bp)


# ==========================================
# LOGIN REQUIRED DECORATOR
# ==========================================
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return fn(*args, **kwargs)
    return wrapper


# ==========================================
# SHARED HISTORY LOADER
# ==========================================
def load_user_history(email, limit=None):
    history_col = app.config["history_col"]

    query = history_col.find({"user_email": email}).sort("created_at", -1)
    if limit is not None:
        query = query.limit(limit)

    records = list(query)

    # Convert UTC → IST for display
    for r in records:
        created_at = r.get("created_at")
        if isinstance(created_at, datetime):
            r["created_at"] = created_at + timedelta(hours=5, minutes=30)

    return records


# ==========================================
# AUTH ROUTES
# ==========================================
@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]

        user = users_col.find_one({"email": email})

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid credentials", "error")
            return render_template("login.html")

        session["user"] = email
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        if users_col.find_one({"email": email}):
            flash("User already exists", "error")
            return render_template("register.html")

        users_col.insert_one({
            "name": name,
            "email": email,
            "password": generate_password_hash(password),
            "role": "user",
            "created_at": datetime.utcnow()
        })

        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==========================================
# APP PAGES
# ==========================================
@app.route("/history")
@login_required
def history():
    email = session["user"]
    records = load_user_history(email)
    return render_template("history.html", records=records)


@app.route("/dashboard")
@login_required
def dashboard():
    email = session.get("user")
    user_doc = users_col.find_one({"email": email})

    user_name = user_doc.get("name", "User")

    prediction = session.get("latest_prediction")

    return render_template(
        "user.html",
        prediction=prediction,
        user_name=user_name   # ✅ IMPORTANT — must match template
    )



@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html")


@app.route("/advice")
@login_required
def advice():
    return render_template("advice.html")


@app.route("/manual")
@login_required
def manual():
    return render_template("manual.html")


@app.route("/dataupload")
@login_required
def dataupload():
    return render_template("dataupload.html")


@app.route("/report")
@login_required
def report():
    email = session["user"]
    records = load_user_history(email)

    user_doc = users_col.find_one({"email": email}) or {}
    user_name = user_doc.get("name", "User")

    return render_template(
        "report.html",
        records=records,
        user_name=user_name
    )




# ==========================================
# PDF GENERATION (ReportLab)
# ==========================================
@app.route("/download-report")
@login_required
def download_report():

    prediction = session.get("latest_prediction")
    email = session.get("user")
    user_doc = users_col.find_one({"email": email})

    patient_name = user_doc.get("name", "Patient")

    if not prediction:
        return "No prediction available"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    # -----------------------
    # TITLE
    # -----------------------
    elements.append(Paragraph("AutoCare AI Medical Risk Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        f"Patient Name: <b>{patient_name}</b>",
        normal_style
    ))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        normal_style
    ))
    elements.append(Spacer(1, 0.5 * inch))

    # -----------------------
    # DISEASE SECTIONS
    # -----------------------
    for disease, data in prediction.get("predictions", {}).items():

        elements.append(Paragraph(f"{disease.upper()} Risk Assessment", heading_style))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph(
            f"<b>Risk Probability:</b> {data.get('risk_percent', 0)}%",
            normal_style
        ))

        elements.append(Paragraph(
            f"<b>Risk Category:</b> {data.get('risk_label', 'N/A')}",
            normal_style
        ))

        elements.append(Paragraph(
            f"<b>Model Used:</b> {data.get('model', 'ML Model')}",
            normal_style
        ))

        elements.append(Spacer(1, 0.3 * inch))

        explanation = f"""
        Based on the submitted health indicators, the AI system estimates a 
        {data.get('risk_label', 'Unknown')} risk level for {disease}. 
        This prediction considers age group, lifestyle factors, 
        metabolic indicators, and cardiovascular stress markers.
        """

        elements.append(Paragraph(explanation, normal_style))
        elements.append(Spacer(1, 0.5 * inch))

    # -----------------------
    # DISCLAIMER
    # -----------------------
    elements.append(Paragraph(
        "<b>Medical Disclaimer:</b>",
        heading_style
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "This report is generated by an AI-based prediction system. "
        "It is intended for educational and preliminary screening purposes only. "
        "It should not replace professional medical diagnosis or consultation.",
        normal_style
    ))

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = \
        "attachment; filename=AutoCare_Medical_Report.pdf"

    return response


# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)