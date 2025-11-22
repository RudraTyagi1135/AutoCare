from flask import Blueprint, request, jsonify
from chatbot.core.genai_client import chat_with_gemini

general_chat_bp = Blueprint("general_chat", __name__)

@general_chat_bp.route("/chat/general", methods=["POST"])
def general_chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message field missing"}), 400

    user_message = data["message"]
    reply = chat_with_gemini(user_message)

    return jsonify({"reply": reply})
