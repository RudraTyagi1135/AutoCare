from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime
from autocare_utils.logging import logging
from machine_learning.prediction.prediction_pipeline import Predictor

manual_bp = Blueprint("manual_bp", __name__, url_prefix="/api")

predictor = Predictor()


def _coerce_bool(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v == 1
    return str(v).strip().lower() in ("1", "true", "t", "yes", "y", "on")


def _map_stress(val):
    if val is None:
        return None
    mapping = {
        "0": "no stress",
        "0.0": "no stress",
        "0.5": "mild",
        "1": "moderate",
        "1.0": "moderate",
        "1.5": "high",
        "2": "severe"
    }
    return mapping.get(str(val).strip(), val)


@manual_bp.route("/manual-entry", methods=["POST"])
def manual_entry():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "message": "No JSON payload received"
            }), 400

        logging.info(f"[manual-entry] Incoming payload: {data}")

        # -------------------------
        # Prepare Input for Model
        # -------------------------
        raw_input = {
            "gender": data.get("gender"),
            "age": data.get("age"),
            "height": data.get("height"),
            "weight": data.get("weight"),
            "systolic": data.get("systolic"),
            "diastolic": data.get("diastolic"),
            "sleeptime": data.get("sleeptime"),
            "chest_pain": _coerce_bool(data.get("chest_pain")),
            "prior_heart_attack": _coerce_bool(data.get("prior_heart_attack")),
            "highchol": _coerce_bool(data.get("highchol")),
            "diffwalk": _coerce_bool(data.get("diffwalk")),
            "physactivity": _coerce_bool(data.get("physactivity")),
            "alcohol": _coerce_bool(data.get("alcohol")),
            "smoking": _coerce_bool(data.get("smoking")),
            "stress_level": _map_stress(data.get("stress_level"))
        }

        # -------------------------
        # Run Predictions
        # -------------------------
        diabetes_pred = predictor.predict("diabetes", raw_input)
        heart_pred = predictor.predict("heart", raw_input)
        stroke_pred = predictor.predict("stroke", raw_input)

        prediction_data = {
            "predictions": {
                "diabetes": diabetes_pred,
                "heart": heart_pred,
                "stroke": stroke_pred
            }
        }

        # -------------------------
        # Store in session (Dashboard use)
        # -------------------------
        session["latest_prediction"] = prediction_data

        # -------------------------
        # Save to MongoDB History
        # -------------------------
        user_email = session.get("user")
        if user_email:
            history_col = current_app.config.get("history_col")
            if history_col is not None:
                history_col.insert_one({
                    "user_email": user_email,
                    "input_data": raw_input,
                    "prediction": prediction_data,
                    "created_at": datetime.utcnow()
                })
            else:
                logging.warning("history_col not configured; skipping history insert")

        logging.info("Prediction stored in session and MongoDB")

        return jsonify({
            "success": True,
            "status": "success"
        })

    except Exception as e:
        logging.exception("❌ Error inside /manual-entry")
        return jsonify({
            "success": False,
            "status": "error",
            "message": str(e)
        }), 500