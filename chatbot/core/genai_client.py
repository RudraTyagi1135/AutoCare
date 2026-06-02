import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from project root
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ GOOGLE_API_KEY missing in .env")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

def chat_with_gemini(message: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
