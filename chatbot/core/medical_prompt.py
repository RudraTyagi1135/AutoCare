# chatbot/core/medical_prompt.py

def build_prediction_explain_prompt(disease: str, prediction_result: dict, shap_explanation: dict, patient_context: str = None) -> str:
    """
    Compose a friendly prompt for the LLM that explains:
      - what the model predicted (risk/probability)
      - short, plain-language explanation using SHAP contributions (if available)
      - suggested lifestyle recommendations (generic)
    """
    prob = prediction_result.get("probability", None)
    label = prediction_result.get("label", None)
    raw_probs = prediction_result.get("raw_probs", None)

    parts = []
    parts.append(f"You're an empathetic medical assistant. A model predicted the risk for *{disease}*.")
    if prob is not None:
        parts.append(f"Model output: predicted probability = {prob:.3f}.")
    if label is not None:
        parts.append(f"Predicted label (0=no,1=yes): {label}.")

    if shap_explanation:
        contribs = shap_explanation.get("explanation") or shap_explanation
        if isinstance(contribs, dict) and "contributions" in contribs:
            top = sorted(contribs["contributions"], key=lambda x: abs(x["contribution"]), reverse=True)[:6]
            parts.append("Key factors contributing to the prediction (largest contributions):")
            for t in top:
                parts.append(f"- {t['feature']}: value {t['value']}, contribution {t['contribution']:.4f}")
        else:
            parts.append("SHAP explanation: " + str(contribs))

    # Add basic advice (generic; not a substitute for a doctor)
    parts.append("\nProvide a short plain-language explanation of what this means for the patient (2-4 sentences), and 4 simple, safe lifestyle suggestions (diet, exercise, follow-up).")
    if patient_context:
        parts.append("\nPatient context: " + patient_context)

    prompt = "\n\n".join(parts)
    return prompt
