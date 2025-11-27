# backend/main.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# ===========================
# Resolve Frontend Directory
# ===========================
THIS_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "frontend"))

# Load .env file
load_dotenv()

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Change for production
if not app.secret_key:
    raise Exception("secret key not found. Set it inside .env")




# ===========================
# MongoDB Setup
# ===========================
MONGO_URI = os.getenv("MONGO_DB_URL")
if not MONGO_URI:
    raise Exception("MongoDB URI not found. Set it inside .env")

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
        try:
            users_col.insert_one({
            "email": email,
            "password": generate_password_hash(password),
            "role": role,
            "created_at": datetime.utcnow()
             })
        except Exception as e:
            flash("Database error while creating account. Try again later.", "error")
            return render_template("register.html")
        # Save registration history
        try:
            register_log_col.insert_one({
            "email": email,
            "role": role,
            "registered_at": datetime.utcnow()
            })
        except Exception as e:
            pass  # not critical, so we don't block the user

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

        try:
            user = users_col.find_one({"email": email})
        except Exception as e:
            flash("Database error while fetching user.", "error")
            return render_template("login.html")
        if user and check_password_hash(user["password"], password) and user["role"] == role:
            session["user"] = email
            session["role"] = role

            try:
                login_log_col.insert_one({
                "email": email,
                "role": role,
                "login_timestamp": datetime.utcnow()
                })
            except Exception as e:
                pass  # do not block login

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

        # Validate numeric fields safely
        def to_int(value):
            try:
                return int(value) if value not in (None, "", " ") else None
            except:
                return None

        def to_float(value):
            try:
                return float(value) if value not in (None, "", " ") else None
            except:
                return None

        def to_bool(value):
            return True if value else False

        # Convert types
        gender = inputs.get("gender")
        age = to_int(inputs.get("age"))
        height = to_float(inputs.get("height"))
        weight = to_float(inputs.get("weight"))
        systolic = to_int(inputs.get("systolic"))
        diastolic = to_int(inputs.get("diastolic"))
        sleep = to_float(inputs.get("sleep"))
        stress = to_float(inputs.get("stress"))

        # Checkbox booleans
        chest_pain = to_bool(inputs.get("chest_pain"))
        heart_attack = to_bool(inputs.get("heart_attack"))
        cholesterol = to_bool(inputs.get("cholesterol"))
        walking_difficulty = to_bool(inputs.get("walking_difficulty"))
        physical_activity = to_bool(inputs.get("physical_activity"))
        alcohol = to_bool(inputs.get("alcohol"))
        smoking = to_bool(inputs.get("smoking"))

        # Required field check
        if age is None or height is None or weight is None:
            flash("Age, height, and weight are required and must be valid numbers.", "error")
            return redirect(url_for("manual_entry"))

        # Generate Demo Scores (you can replace later)
        heart_score = random.randint(30, 79)
        stroke_score = random.randint(10, 49)
        diabetes_score = random.randint(5, 34)

        # Build final record with correct datatypes
        record = {
            "email": session.get("user"),
            "role": session.get("role"),
            "timestamp": datetime.utcnow(),
            "input_values": {
                "gender": gender,
                "age": age,
                "height": height,
                "weight": weight,
                "systolic": systolic,
                "diastolic": diastolic,
                "sleep": sleep,
                "chest_pain": chest_pain,
                "heart_attack": heart_attack,
                "cholesterol": cholesterol,
                "walking_difficulty": walking_difficulty,
                "physical_activity": physical_activity,
                "alcohol": alcohol,
                "smoking": smoking,
                "stress": stress
            },
            "scores": {
                "heart": f"{heart_score}%",
                "stroke": f"{stroke_score}%",
                "diabetes": f"{diabetes_score}%"
            }
        }

        # Save safely
        try:
            inserted_id = manual_col.insert_one(record).inserted_id
        except Exception as e:
            flash("Database error while saving data. Try again later.", "error")
            return redirect(url_for("manual_entry"))

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
    app.run(debug=False, host="127.0.0.1", port=5000)
