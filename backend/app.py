from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes.chatbot_general import general_chat_bp
from routes.chatbot_medical import medical_bp  
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Register chatbot route
app.register_blueprint(general_chat_bp, url_prefix="/api")
# app.register_blueprint(medical_bp, url_prefix="/api")
app.register_blueprint(medical_bp) 

# -------------------------------------------------------
#  Serve Frontend (chatbot UI)
# -------------------------------------------------------
ROOT_DIR = Path(_file_).resolve().parent.parent       # AutoCare/
FRONTEND_DIR = ROOT_DIR / "frontend" / "chatbot_general"

@app.route("/chat-ui")
def serve_chat_ui():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/chat-ui/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/")
def home():
    return jsonify({"message": "AutoCare Flask backend running!"})

# ---------------------------------------------
# Serve Medical Chatbot UI
# ---------------------------------------------
MEDICAL_UI_DIR = ROOT_DIR / "frontend" / "chatbot_medical"

@app.route("/medical-chat-ui")
def serve_medical_ui():
    return send_from_directory(MEDICAL_UI_DIR, "index.html")

@app.route("/medical-chat-ui/<path:filename>")
def serve_medical_static(filename):
    return send_from_directory(MEDICAL_UI_DIR, filename)


if __name__ == "_main_":
    app.run(host="127.0.0.1", port=9000, debug=True)