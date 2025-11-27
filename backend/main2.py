# backend/main.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from datetime import datetime
import random
import os

from flask_cors import CORS

# ===========================
# Resolve Frontend Directory
# ===========================
THIS_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "frontend"))

# Chatbot route imports
from routes.chatbot_general import general_chat_bp
from routes.chatbot_medical import medical_bp

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)
CORS(app)
app.secret_key = "autocare_secret_key"


# ===========================
# MongoDB Setup
# ===========================
MONGO_URI = "mongodb+srv://rudratyagi777_db_user:rudra1135@autocare.gilugwr.mongodb.net/?appName=AutoCare"
client = MongoClient(MONGO_URI)
db = client["History"]

users_col = db["users"]
register_log_col = db["register_logs"]
login_log_col = db["login_logs"]
manual_col = db["manual_history"]


# ===========================
# REGISTER CHATBOT ROUTES
# ===========================
app.register_blueprint(general_chat_bp, url_prefix="/api")
app.register_blueprint(medical_bp)   # already includes /api/medical


# ===========================
# LOGIN PROTECTION DECORATOR
# ===========================
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if "user" not in session:
                flash("Please log in.", "error")
                return redirect(url_for("login"))

            if role and session.get("role") != role:
                flash("Access denied.", "error")
                return redirect(url_for("dashboard"))

            g.user = session["user"]
            g.role = session["role"]
            return fn(*args, **kwargs)
        return decorated
    return wrapper


# ===========================
# HOME
# ===========================
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ===========================
# REGISTER
# ===========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]
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
            "timestamp": datetime.utcnow()
        })

        flash("Registration successful. Login now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ===========================
# LOGIN
# ===========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        role = request.form.get("role", "user")

        user = users_col.find_one({"email": email})

        if user and check_password_hash(user["password"], password) and user["role"] == role:
            session["user"] = email
            session["role"] = role

            login_log_col.insert_one({
                "email": email,
                "role": role,
                "timestamp": datetime.utcnow()
            })

            flash("Login successful", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "error")

    return render_template("login.html")


# ===========================
# DASHBOARD
# ===========================
@app.route("/dashboard")
@login_required()
def dashboard():
    template_file = f"{session.get('role', 'user')}.html"
    if not os.path.exists(os.path.join(FRONTEND_DIR, template_file)):
        template_file = "user.html"

    return render_template(template_file)


# ===========================
# MANUAL ENTRY
# ===========================
@app.route("/manual-entry", methods=["GET", "POST"])
@login_required()
def manual_entry():
    if request.method == "POST":
        inputs = request.form.to_dict()

        record = {
            "email": session["user"],
            "role": session["role"],
            "timestamp": datetime.utcnow(),
            "input_values": inputs,
            "scores": {
                "heart": f"{random.randint(30,79)}%",
                "stroke": f"{random.randint(10,49)}%",
                "diabetes": f"{random.randint(5,34)}%"
            }
        }

        manual_col.insert_one(record)
        session["last_manual"] = record

        flash("Form submitted!", "success")
        return redirect(url_for("dashboard"))

    return render_template("manual.html")


# ===========================
# LOGOUT
# ===========================
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


# ===========================
# RUN APP
# ===========================
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
