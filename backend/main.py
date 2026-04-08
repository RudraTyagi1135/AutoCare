# backend/main.py
# ================================
# AutoCare - FINAL MAIN BACKEND
# (serves templates from frontend/templates and css/js under /css & /js)
# ================================
import os
from pathlib import Path
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv
from functools import wraps
from flask_cors import CORS

# -----------------------------
# PATH CONFIG
# -----------------------------
ROOT = Path(__file__).resolve().parent.parent    # project root (AutoCare/)
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_TEMPLATES = FRONTEND_DIR / "templates"
FRONTEND_STYLE = FRONTEND_DIR / "style"          # contains css/ and js/
CHATBOT_GENERAL_DIR = FRONTEND_DIR / "chatbot_general"
CHATBOT_MEDICAL_DIR = FRONTEND_DIR / "chatbot_medical"

print("AutoCare Backend Running")
print("Templates:", FRONTEND_TEMPLATES)
print("Style (css/js):", FRONTEND_STYLE)
print("Chatbot general dir:", CHATBOT_GENERAL_DIR)
print("Chatbot medical dir:", CHATBOT_MEDICAL_DIR)

# -----------------------------
# APP INIT
# -----------------------------
# Use templates folder explicitly and DO NOT rely on Flask's built-in static route.
# We'll add explicit routes so existing template relative links like "css/..." keep working.
app = Flask(
    __name__,
    template_folder=str(FRONTEND_TEMPLATES),
    static_folder=None   # disable built-in static to avoid collisions — we'll serve custom routes
)

CORS(app)
load_dotenv(ROOT / ".env")

app.secret_key = os.getenv("FLASK_SECRET_KEY") or "dev-secret-for-local"  # replace in prod

# -----------------------------
# MONGO INIT (safe)
# -----------------------------
MONGO_URI = os.getenv("MONGO_DB_URL")
if not MONGO_URI:
    print("⚠️  Warning: MONGO_DB_URL not set in .env — continuing without DB for local UI testing")
    client = None
    db = None
    users_col = None
    manual_col = None
else:
    client = MongoClient(MONGO_URI)
    db = client.get_database("History")
    users_col = db["users"]
    manual_col = db["manual_history"]

# -----------------------------
# BLUEPRINTS (import after app created)
# -----------------------------
# if these fail to import, app start will fail and you'll see the error
try:
    from routes.chatbot_general import general_chat_bp
    from routes.chatbot_medical import medical_bp
    from routes.manual_entry import manual_bp
except Exception as e:
    # Print full error to console, but allow the server to start for UI debugging (optional)
    print("Failed to import one or more blueprints:", e)
    raise

app.register_blueprint(general_chat_bp, url_prefix="/api")
# medical_bp likely defines its own prefix — register as-is
app.register_blueprint(medical_bp)
app.register_blueprint(manual_bp, url_prefix="/api")

# -----------------------------
# Serve frontend static assets (css/js) at root paths used by templates
# Templates refer to "css/..."/"js/..." (relative to site root),
# so we expose those routes to match the existing HTML.
# -----------------------------
@app.route("/css/<path:filename>")
def serve_css(filename):
    """Serve CSS files from frontend/style/css/"""
    css_dir = FRONTEND_STYLE / "css"
    return send_from_directory(css_dir, filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    """Serve JS files from frontend/style/js/"""
    js_dir = FRONTEND_STYLE / "js"
    return send_from_directory(js_dir, filename)

@app.route("/images/<path:filename>")
def serve_images(filename):
    """Optional: image assets if you have them under style/images/"""
    img_dir = FRONTEND_STYLE / "images"
    return send_from_directory(img_dir, filename)

# Serve the chatbot standalone folders (they contain index.html + assets)
@app.route("/chatbot_general/<path:filename>")
def serve_chatbot_general(filename):
    return send_from_directory(CHATBOT_GENERAL_DIR, filename)

@app.route("/chatbot_medical/<path:filename>")
def serve_chatbot_medical(filename):
    return send_from_directory(CHATBOT_MEDICAL_DIR, filename)

# If someone requests the chatbot root, serve index.html
@app.route("/chat-ui")
def chat_ui_root():
    return send_from_directory(CHATBOT_GENERAL_DIR, "index.html")

@app.route("/medical-chat-ui")
def med_chat_ui_root():
    return send_from_directory(CHATBOT_MEDICAL_DIR, "index.html")

# -----------------------------
# Simple login_required decorator
# -----------------------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return fn(*args, **kwargs)
    return wrapper

# -----------------------------
# AUTH ROUTES (keep as-is)
# -----------------------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if users_col is None:
            flash("Database not configured (MONGO_DB_URL missing).", "error")
            return render_template("login.html")

        user = users_col.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid credentials", "error")
            return render_template("login.html")

        session["user"] = email
        flash("Login successful!", "success")
        return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        if password != confirm:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        if users_col is not None:
            users_col.insert_one({
                "email": email,
                "password": generate_password_hash(password)
            })
        else:
            print("Skipped DB insert because MONGO_DB_URL missing (local dev)")

        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -----------------------------
# FRONTEND PAGES (render templates)
# -----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("user.html")

@app.route("/advice")
@login_required
def advice_page():
    return render_template("advice.html")

@app.route("/chat")
@login_required
def chat_page():
    return render_template("chat.html")

@app.route("/manual")
@login_required
def manual_page():
    return render_template("manual.html")

@app.route("/report")
@login_required
def report_page():
    return render_template("report.html")

@app.route("/dataupload")
@login_required
def dataupload_page():
    return render_template("dataupload.html")

# -----------------------------
# Helpful API: return a saved manual-entry record (by id)
# (If you store ObjectId, you should cast/convert when querying)
# -----------------------------
@app.route("/api/last-manual/<string:record_id>", methods=["GET"])
@login_required
def api_get_manual(record_id):
    if manual_col is None:
        return jsonify({"success": False, "error": "DB not configured"}), 500
    try:
        rec = manual_col.find_one({"_id": record_id})
        return jsonify({"success": True, "record": rec})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------
# RUN SERVER (single app.run only)
# -----------------------------
if __name__ == "__main__": 
    # Ensure only one run point exists to avoid socket errors on Windows
    print("\nStarting server: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
