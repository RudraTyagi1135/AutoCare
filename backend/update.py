import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
import logging

from certifi import where as certifi_where
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    make_response,
)
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------------------------------
# PROJECT ROOT
# ------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# ------------------------------------------
# PATH CONFIG
# ------------------------------------------
TEMPLATES_DIR = ROOT / "frontend" / "templates"
STATIC_DIR = ROOT / "frontend" / "style"

# ------------------------------------------
# LOAD ENV
# ------------------------------------------
load_dotenv(ROOT / ".env")
# ------------------------------------------
# LOGGING
# ------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("🚀 Auto Backend Running")
logger.info(f"Templates: {TEMPLATES_DIR}")
logger.info(f"Static: {STATIC_DIR}")


def is_placeholder(value: str | None) -> bool:
    if not value:
        return True
    lowered = value.strip().lower()
    placeholder_tokens = (
        "your_mongodb_connection_string",
        "your mongodb connection string",
        "replace_with_your_mongodb_uri",
        "mongodb_connection_string",
        "mongodb_uri_here",
        "your_secret_key",
        "secret_key_here",
        "change_me",
    )
    return any(token in lowered for token in placeholder_tokens)


# ------------------------------------------
# APP INIT
# ------------------------------------------
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path="/style",
)

CORS(app)

secret_key = os.getenv("FLASK_SECRET_KEY")
if is_placeholder(secret_key):
    raise Exception(
        "Missing or placeholder FLASK_SECRET_KEY in .env. "
        "Add a real secret key."
    )

app.secret_key = secret_key

# ------------------------------------------
# DATABASE
# ------------------------------------------
MONGO_URI = os.getenv("MONGO_DB_URL")
if is_placeholder(MONGO_URI):
    raise Exception(
        "Missing or placeholder MONGO_DB_URL in .env. "
        "Replace it with your real MongoDB Atlas URI."
    )

try:
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi_where(),
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
    )

    client.admin.command("ping")
    logger.info("MongoDB connection successful")

except ServerSelectionTimeoutError as exc:
    raise Exception(
        "MongoDB connection failed. Check MONGO_DB_URL in .env. "
        f"Details: {exc}"
    ) from exc

db = client["History"]
users_col = db["users"]
history_col = db["prediction_history"]

app.config["DB"] = db
app.config["users_col"] = users_col
app.config["history_col"] = history_col

# ------------------------------------------
# REGISTER BLUEPRINTS
# ------------------------------------------
from routes.chatbot_general import general_chat_bp
from routes.chatbot_medical import medical_bp
from routes.manual_entry import manual_bp

app.register_blueprint(general_chat_bp, url_prefix="/api")
app.register_blueprint(medical_bp)
app.register_blueprint(manual_bp)
logger.info("All blueprints registered successfully")

# ------------------------------------------
# LOGIN REQUIRED DECORATOR
# ------------------------------------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return fn(*args, **kwargs)

    return wrapper

# ------------------------------------------
# SHARED HISTORY LOADER
# ------------------------------------------
def load_user_history(email, limit=None):
    query = history_col.find({"user_email": email}).sort("created_at", -1)
    if limit is not None:
        query = query.limit(limit)

    records = list(query)

    for r in records:
        created_at = r.get("created_at")
        if isinstance(created_at, datetime):
            r["created_at"] = created_at + timedelta(hours=5, minutes=30)

    return records

# ------------------------------------------
# AUTH ROUTES
# ------------------------------------------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter email and password.", "error")
            return render_template("login.html", active_tab="login")

        user = users_col.find_one({"email": email})

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid credentials", "error")
            return render_template("login.html", active_tab="login")

        session["user"] = email
        session["role"] = user.get("role", "user")
        session["name"] = user.get("name", "User")

        flash("Login successful!", "success")
        return redirect("/dashboard")

    return render_template("login.html", active_tab="login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm:
            flash("Please fill all fields.", "error")
            return render_template("login.html", active_tab="register")

        if password != confirm:
            flash("Passwords do not match", "error")
            return render_template("login.html", active_tab="register")

        if users_col.find_one({"email": email}):
            flash("User already exists", "error")
            return render_template("login.html", active_tab="register")

        users_col.insert_one(
            {
                "name": name,
                "email": email,
                "password": generate_password_hash(password),
                "role": "user",
                "created_at": datetime.utcnow(),
            }
        )

        flash("Registration successful!", "success")
        return redirect("/login")

    return render_template("login.html", active_tab="register")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------------------------------
# APP PAGES
# ------------------------------------------
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
    user_doc = users_col.find_one({"email": email}) or {}

    user_name = user_doc.get("name", "User")
    prediction = session.get("latest_prediction")

    return render_template(
        "user.html",
        prediction=prediction,
        user_name=user_name,
    )


@app.route("/chat")
@login_required
def chat():
    email = session.get("user")
    user_doc = users_col.find_one({"email": email}) or {}

    return render_template(
        "chat.html",
        user_name=user_doc.get("name", "User")
    )


@app.route("/advice")
@login_required
def advice():
    email = session.get("user")
    user_doc = users_col.find_one({"email": email}) or {}

    return render_template(
        "advice.html",
        user_name=user_doc.get("name", "User")
    )


@app.route("/manual")
@login_required
def manual():
    return render_template("manual.html")


@app.route("/dataupload")
@login_required
def dataupload():
    email = session.get("user")
    user_doc = users_col.find_one({"email": email}) or {}

    return render_template(
        "dataupload.html",
        user_name=user_doc.get("name", "User")
    )


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
        user_name=user_name,
    )

# ------------------------------------------
# PDF GENERATION
# ------------------------------------------
@app.route("/download-report")
@login_required
def download_report():
    prediction = session.get("latest_prediction")
    email = session.get("user")
    user_doc = users_col.find_one({"email": email}) or {}
    patient_name = user_doc.get("name", "Patient")

    if not prediction:
        return "No prediction available", 400

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    elements.append(Paragraph("AutoCare AI Medical Risk Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(
        Paragraph(f"Patient Name: <b>{patient_name}</b>", normal_style)
    )
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            normal_style,
        )
    )
    elements.append(Spacer(1, 0.5 * inch))

    for disease, data in prediction.get("predictions", {}).items():
        elements.append(Paragraph(f"{disease.upper()} Risk Assessment", heading_style))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(
            Paragraph(
                f"<b>Risk Probability:</b> {data.get('risk_percent', 0)}%",
                normal_style,
            )
        )

        elements.append(
            Paragraph(
                f"<b>Risk Category:</b> {data.get('risk_label', 'N/A')}",
                normal_style,
            )
        )

        elements.append(
            Paragraph(
                f"<b>Model Used:</b> {data.get('model', 'ML Model')}",
                normal_style,
            )
        )

        elements.append(Spacer(1, 0.3 * inch))

        explanation = f"""
        Based on the submitted health indicators, the AI system estimates a
        {data.get('risk_label', 'Unknown')} risk level for {disease}.
        This prediction considers age group, lifestyle factors,
        metabolic indicators, and cardiovascular stress markers.
        """

        elements.append(Paragraph(explanation, normal_style))
        elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph("<b>Medical Disclaimer:</b>", heading_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(
        Paragraph(
            "This report is generated by an AI-based prediction system. "
            "It is intended for educational and preliminary screening purposes only. "
            "It should not replace professional medical diagnosis or consultation.",
            normal_style,
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        "attachment; filename=Auto_Medical_Report.pdf"
    )

    return response

# ------------------------------------------
# ERROR HANDLERS
# ------------------------------------------
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


# ------------------------------------------
# RUN SERVER
# ------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)