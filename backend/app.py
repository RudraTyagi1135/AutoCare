from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

# ---- Blueprints ----
from routes.chatbot_general import general_chat_bp
from routes.chatbot_medical import medical_bp
from backend.routes.manual_entry import manual_bp  # Prediction API

# --------- App Init ---------
app = Flask(__name__)
CORS(app)

# --------- Register Blueprints ---------
app.register_blueprint(general_chat_bp, url_prefix="/api")
app.register_blueprint(medical_bp, url_prefix="/api")
app.register_blueprint(manual_bp, url_prefix="/api")

# --------- Frontend Paths ---------
ROOT_DIR = Path(__file__).resolve().parent.parent

CHATBOT_GENERAL_DIR = ROOT_DIR / "frontend" / "chatbot_general"
CHATBOT_MEDICAL_DIR = ROOT_DIR / "frontend" / "chatbot_medical"
MANUAL_UI_DIR = ROOT_DIR / "frontend"

# --------- Chat UI ---------
@app.route("/chat-ui")
def serve_chat_ui():
  return send_from_directory(CHATBOT_GENERAL_DIR, "index.html")

@app.route("/chat-ui/<path:filename>")
def serve_static_chat(filename):
  return send_from_directory(CHATBOT_GENERAL_DIR, filename)

# --------- Medical Chat UI ---------
@app.route("/medical-chat-ui")
def serve_medical_ui():
  return send_from_directory(CHATBOT_MEDICAL_DIR, "index.html")

@app.route("/medical-chat-ui/<path:filename>")
def serve_static_medical(filename):
  return send_from_directory(CHATBOT_MEDICAL_DIR, filename)

# --------- Manual Entry Health UI ---------
@app.route("/manual")
def manual_page():
  return send_from_directory(MANUAL_UI_DIR, "manual.html")

@app.route("/manual/<path:filename>")
def manual_static(filename):
  return send_from_directory(MANUAL_UI_DIR, filename)

# --------- Root Endpoint ---------
@app.route("/")
def home():
  return jsonify({"message": "AutoCare Flask backend running!"})


# --------- Run Server ---------
if __name__ == "__main__":
    print("\n================= 🚀 AUT0CARE BACKEND RUNNING =================\n")
    print(" ➤ Local Server:        http://127.0.0.1:9000")
    print(" ➤ Manual Form UI:      http://127.0.0.1:9000/manual")
    print(" ➤ API Test Endpoint:   http://127.0.0.1:9000/api/manual-entry")
    print(" ===============================================================\n")

    app.run(host="127.0.0.1", port=9000, debug=True)
