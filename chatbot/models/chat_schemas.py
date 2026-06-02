# chatbot/models/chat_schemas.py
from dataclasses import dataclass

class ChatRequest:
    def __init__(self, message: str):
        self.message = message
from dataclasses import dataclass

@dataclass
class MedicalPredictRequest:
    disease: str
    features: dict

@dataclass
class MedicalExplainRequest:
    disease: str
    features: dict
    patient_context: str = None        
