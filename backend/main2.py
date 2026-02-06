from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from datetime import datetime
import random
import os
from pathlib import Path
from flask_cors import CORS
from dotenv import load_dotenv

from routes.chatbot_general import general_chat_bp
from routes.chatbot_medical import medical_bp


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "style"

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

MONGO_URI = os.getenv("MONGO_DB_URL")
if not MONGO_URI:
    raise Exception("Missing MONGO_DB_URL in .env")

client = MongoClient(MONGO_URI)
db = client["History"]

users_col = db["users"]
register_log_col = db["register_logs"]
login_log_col = db["login_logs"]
manual_col = db["manual_history"]

app.register_blueprint(general_chat_bp, url_prefix="/api")
app.register_blueprint(medical_bp)


def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user" not in session:
                flash("Please log in.", "error")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied.", "error")
                return redirect(url_for("dashboard"))
            g.user = session.get("user")
            g.role = session.get("role")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        role = request.form.get("role", "user")

        if password != confirm:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        if users_col.find_one({"email": email}):
            flash("User already exists", "error")
            return render_template("register.html")

        users_col.insert_one({
            "email": email,
            "password": generate_password_hash(password),
            "role": role,
            "created_at": datetime.utcnow()
        })

        register_log_col.insert_one({
            "email": email,
            "role": role,
            "registered_at": datetime.utcnow()
        })

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password")
        role = request.form.get("role", "user")

        user = users_col.find_one({"email": email})
        if not user:
            flash("Invalid email or password", "error")
            return render_template("login.html")

        if not check_password_hash(user["password"], password):
            flash("Incorrect password", "error")
            return render_template("login.html")

        if user["role"] != role:
            flash("Invalid role selected", "error")
            return render_template("login.html")

        session["user"] = email
        session["role"] = role

        login_log_col.insert_one({
            "email": email,
            "role": role,
            "timestamp": datetime.utcnow()
        })

        flash("Login successful!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required()
def dashboard():
    role = session.get("role", "user")
    file = f"{role}.html"

    if not (TEMPLATES_DIR / file).exists():
        file = "user.html"

    return render_template(file)


@app.route("/manual-entry", methods=["GET", "POST"])
@login_required()
def manual_entry():
    if request.method == "POST":
        raw = request.form.to_dict()

        def to_int(v):
            try: return int(v)
            except: return None

        def to_float(v):
            try: return float(v)
            except: return None

        def to_bool(v):
            return True if v and str(v).lower() in ("1", "true", "yes", "on") else False

        age = to_int(raw.get("age"))
        height = to_float(raw.get("height"))
        weight = to_float(raw.get("weight"))

        if age is None or height is None or weight is None:
            flash("Invalid numeric input", "error")
            return redirect(url_for("manual_entry"))

        bmi = round(weight / ((height / 100) ** 2), 2)

        result = {
            "heart": f"{random.randint(30, 79)}%",
            "stroke": f"{random.randint(10, 49)}%",
            "diabetes": f"{random.randint(5, 34)}%"
        }

        manual_col.insert_one({
            "email": session["user"],
            "role": session["role"],
            "timestamp": datetime.utcnow(),
            "bmi": bmi,
            "scores": result
        })

        flash("Form submitted successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("manual.html")


@app.route("/logout")
@login_required()
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
