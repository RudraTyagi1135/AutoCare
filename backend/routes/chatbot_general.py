from flask import Blueprint, request, jsonify
from chatbot.core.genai_client import chat_with_gemini

general_chat_bp = Blueprint("general_chat_bp", __name__, url_prefix="/api")

@general_chat_bp.route("/chat/general", methods=["POST"])
def general_chat():
    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({
            "success": False,
            "error": "No message provided"
        }), 400

    # 🔥 Call Gemini
    reply = chat_with_gemini(user_msg)

    return jsonify({
        "success": True,
        "reply": reply
    })
