# backend/routes/chatbot_medical.py
from flask import Blueprint, request, jsonify
from chatbot.core.genai_client import chat_with_gemini

medical_bp = Blueprint("medical", __name__, url_prefix="/api/medical")

@medical_bp.route("/chat", methods=["POST"])
def medical_chat():
    payload = request.get_json() or {}
    message = payload.get("message")

    if not message:
        return jsonify({"success": False, "error": "No message provided"}), 400

    try:
        reply = chat_with_gemini(
            f"You are a medical assistant. Answer user query professionally and clearly.\n\nUser: {message}"
        )
        return jsonify({"success": True, "reply": reply})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
