# backend/main.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime
import os

# Resolve frontend directory relative to this file
THIS_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "frontend"))

# Use the frontend folder for templates and static files
app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path=""  # serve static files at root (e.g. /css/, /js/, /login.html)
)
app.secret_key = "autocare_secret_key"  # change this to a secure random key in production

# ===========================
# Dummy users database (email -> { password: hashed, role: "user"|"doctor" })
# ===========================
USERS = {
    "user@example.com": {"password": generate_password_hash("password"), "role": "user"},
    "doctor@example.com": {"password": generate_password_hash("password"), "role": "doctor"},
}

# ===========================
# Helper & Decorators
# ===========================
def login_required(role=None):
    """Decorator to protect routes. Optionally checks for role."""
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if "user" not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("login"))
            g.user = session.get("user")
            g.role = session.get("role")
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# ===========================
# ROUTES
# ===========================
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# Convenience endpoints you can link from frontend for switching pages
@app.route("/go-register")
def go_register():
    """Simple redirect endpoint — useful if you want a backend link to the register page."""
    return redirect(url_for("register"))

@app.route("/go-login")
def go_login():
    """Simple redirect endpoint — useful if you want a backend link to the login page."""
    return redirect(url_for("login"))

# Serve login page and handle login POST
@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, go to dashboard
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user").strip()

        if not email or not password:
            flash("Please fill in both fields.", "error")
            return render_template("login.html")

        user = USERS.get(email)
        # authenticate against USERS dict (passwords are hashed)
        if user and check_password_hash(user["password"], password) and user["role"] == role:
            session["user"] = email
            session["role"] = role
            flash(f"Welcome, {email}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials or role. Please try again.", "error")
            return render_template("login.html")

    # GET -> show login
    return render_template("login.html")

# Serve register page and handle registration POST
@app.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in, sent to dashboard
    if "user" in session:
        flash("You are already logged in.", "info")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "user").strip()

        # basic validation
        if not email or not password or not confirm_password or not role:
            flash("Please fill all fields.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if email in USERS:
            flash("Account already exists for this email.", "error")
            return render_template("register.html")

        # create user (demo; in production use a DB)
        USERS[email] = {
            "password": generate_password_hash(password),
            "role": role
        }

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("login"))

    # GET -> show register
    return render_template("register.html")

# Dashboard — picks template based on role
@app.route("/dashboard")
@login_required()
def dashboard():
    role = session.get("role", "user")
    template_name = f"{role}.html"
    # check if the template file exists in the frontend folder
    if not os.path.exists(os.path.join(FRONTEND_DIR, template_name)):
        flash(f"Template '{template_name}' not found — showing user view instead.", "info")
        template_name = "user.html"
    last_manual = session.get("last_manual")
    return render_template(template_name, user=session.get("user"), last_manual=last_manual)

@app.route("/logout")
@login_required()
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ===========================
# Manual Entry Route
# ===========================
@app.route("/manual-entry", methods=["GET", "POST"])
@login_required()
def manual_entry():
    if request.method == "POST":
        inputs = {k: v for k, v in request.form.items()}
        if not inputs:
            flash("Please submit the manual form with at least one value.", "error")
            return render_template("manual.html", values={})

        heart_score = int(random.random() * 50 + 30)       # 30–79%
        stroke_score = int(random.random() * 40 + 10)      # 10–49%
        diabetes_score = int(random.random() * 30 + 5)     # 5–34%

        result = {
            "submitted_by": session.get("user"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "inputs": inputs,
            "scores": {
                "heart": f"{heart_score}%",
                "stroke": f"{stroke_score}%",
                "diabetes": f"{diabetes_score}%"
            },
            "drivers": {
                "heart": ["Age", "Cholesterol"],
                "stroke": ["BP", "Smoking"],
                "diabetes": ["Glucose", "Weight"]
            }
        }

        session["last_manual"] = result
        flash("Manual entry submitted — analysis saved and will appear on the dashboard.", "success")
        return redirect(url_for("dashboard"))

    return render_template("manual.html")

# Keep compatibility route if something links to manual.html specifically
@app.route("/manual.html")
def manual_html_redirect():
    return redirect(url_for("manual_entry"))

# Optional: convenience routes to directly serve html files (if you want /login.html etc.)
@app.route("/<page>.html")
def serve_page(page):
    allowed = {"login", "register", "manual", "user"}
    filename = f"{page}.html"
    if page in allowed and os.path.exists(os.path.join(FRONTEND_DIR, filename)):
        return render_template(filename)
    return "Not found", 404

# ===========================
# RUN APP
# ===========================
if __name__ == "__main__":
    # Run on localhost:5000
    app.run(debug=True, host="127.0.0.1", port=5000)
