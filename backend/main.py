# backend/main.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import random
from datetime import datetime
import os

# ===========================
# Resolve Frontend Directory
# ===========================
THIS_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "frontend"))

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)
app.secret_key = "autocare_secret_key"  # Change for production


# ===========================
# MongoDB Setup
# ===========================
MONGO_URI = "mongodb+srv://rudratyagi777_db_user:rudra1135@autocare.gilugwr.mongodb.net/?appName=AutoCare"  # Replace if using Atlas
client = MongoClient(MONGO_URI)
db = client["History"]

users_col = db["users"]             # Registered users
register_log_col = db["register_logs"]  # Registration history
login_log_col = db["login_logs"]    # Login history
manual_col = db["manual_history"]   # Manual form submissions


# ===========================
# LOGIN PROTECTION DECORATOR
# ===========================
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if "user" not in session:
                flash("Please log in.", "error")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied.", "error")
                return redirect(url_for("dashboard"))
            g.user = session.get("user")
            g.role = session.get("role")
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# ===========================
# HOME → LOGIN REDIRECT
# ===========================
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ===========================
# REGISTER ROUTE (MongoDB)
# ===========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        flash("You are already logged in.", "info")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        role = request.form.get("role", "user").strip()

        if not email or not password or not confirm_password:
            flash("Fill all fields.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if users_col.find_one({"email": email}):
            flash("User already exists!", "error")
            return render_template("register.html")

        # Insert new user
        users_col.insert_one({
            "email": email,
            "password": generate_password_hash(password),
            "role": role,
            "created_at": datetime.utcnow()
        })

        # Save registration history
        register_log_col.insert_one({
            "email": email,
            "role": role,
            "registered_at": datetime.utcnow()
        })

        flash("Registration successful. Login now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ===========================
# LOGIN ROUTE (MongoDB)
# ===========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user").strip()

        if not email or not password:
            flash("Enter email and password.", "error")
            return render_template("login.html")

        user = users_col.find_one({"email": email})

        if user and check_password_hash(user["password"], password) and user["role"] == role:
            session["user"] = email
            session["role"] = role

            login_log_col.insert_one({
                "email": email,
                "role": role,
                "login_timestamp": datetime.utcnow()
            })

            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials or role.", "error")
            return render_template("login.html")

    return render_template("login.html")


# ===========================
# DASHBOARD ROUTE
# ===========================
@app.route("/dashboard")
@login_required()
def dashboard():
    role = session.get("role", "user")
    template_name = f"{role}.html"

    if not os.path.exists(os.path.join(FRONTEND_DIR, template_name)):
        template_name = "user.html"  # fallback

    last_manual = session.get("last_manual")
    return render_template(template_name, user=session.get("user"), last_manual=last_manual)


# ===========================
# MANUAL ENTRY (MongoDB)
# ===========================
@app.route("/manual-entry", methods=["GET", "POST"])
@login_required()
def manual_entry():
   if request.method == "POST":
    inputs = {k: v for k, v in request.form.items()}

    if not inputs:
        flash("Please fill at least one value.", "error")
        return render_template("manual.html")

    # Generate Demo Scores
    heart_score = random.randint(30, 79)
    stroke_score = random.randint(10, 49)
    diabetes_score = random.randint(5, 34)

    record = {
        "email": session.get("user"),
        "role": session.get("role"),
        "timestamp": datetime.utcnow(),
        "input_values": {
            "gender": inputs.get("gender"),
            "age": inputs.get("age"),
            "height": inputs.get("height"),
            "weight": inputs.get("weight"),
            "systolic": inputs.get("systolic"),
            "diastolic": inputs.get("diastolic"),
            "sleep": inputs.get("sleep"),
            "chest_pain": "yes" if inputs.get("chest_pain") else "no",
            "heart_attack": "yes" if inputs.get("heart_attack") else "no",
            "cholesterol": "yes" if inputs.get("cholesterol") else "no",
            "walking_difficulty": "yes" if inputs.get("walking_difficulty") else "no",
            "physical_activity": "yes" if inputs.get("physical_activity") else "no",
            "alcohol": "yes" if inputs.get("alcohol") else "no",
            "smoking": "yes" if inputs.get("smoking") else "no",
            "stress": inputs.get("stress")
        },
        "scores": {
            "heart": f"{heart_score}%",
            "stroke": f"{stroke_score}%",
            "diabetes": f"{diabetes_score}%"
        }
    }

    inserted_id = manual_col.insert_one(record).inserted_id
    session["last_manual"] = str(inserted_id)

    flash("Form submitted & saved successfully.", "success")
    return redirect(url_for("dashboard"))



 
# ===========================
# LOGOUT
# ===========================
@app.route("/logout")
@login_required()
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


# ===========================
# Run App
# ===========================
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
