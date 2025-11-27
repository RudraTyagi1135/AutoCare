# backend/routes/manual_entry.py

from flask import Blueprint, request, jsonify
from autocare_utils.logging import logging
from machine_learning.prediction.prediction_pipeline import Predictor
from autocare_utils.exception import AutoCareException
import sys

manual_bp = Blueprint("manual_bp", __name__)

# Single global predictor instance
predictor = Predictor()


def _map_stress_value(val):
    if val is None:
        return None
    s = str(val).strip().lower()

    mapping = {
        "0":"no stress","0.0":"no stress","no stress":"no stress",
        "0.5":"mild","mild":"mild",
        "1":"moderate","1.0":"moderate","moderate":"moderate",
        "1.5":"high","high":"high",
        "2":"severe","severe":"severe",
    }
    return mapping.get(s, s)



def _coerce_bool_like(v):
    """Return True/False from checkbox/form/json input"""
    if v is None:
        return False
    if isinstance(v, (bool, int)):
        return bool(v)
    s = str(v).strip().lower()
    return s in ("1", "true", "t", "yes", "y", "on")


@manual_bp.route("/manual-entry", methods=["POST"])
def manual_entry():
    """
    Accepts JSON (preferred) or form-encoded POST from manual.html.
    Produces predictions for diabetes, heart, stroke using Predictor.predict.
    """
    try:
        # Accept JSON first, fallback to form
        data = request.get_json(silent=True)
        if data is None:
            data = request.form.to_dict(flat=True)

        logging.info(f"[manual-entry] incoming payload: {data}")

        # Normalize input names to what encode_raw_input expects
        gender = data.get("gender") or data.get("sex") or ""
        age = data.get("age")
        height = data.get("height") or data.get("height_cm") or data.get("heightCm")
        weight = data.get("weight") or data.get("weight_kg") or data.get("weightKg")
        systolic = data.get("systolic")
        diastolic = data.get("diastolic")

        # sleep value may be named "sleep" in the JS payload
        sleeptime = (
            data.get("sleep")
            or data.get("sleeptime")
            or data.get("sleep_hours")
        )

        # Checkboxes / booleans
        chest_pain = _coerce_bool_like(data.get("chest_pain") or data.get("chk_chest"))
        prior_heart_attack = _coerce_bool_like(
            data.get("prior_heart_attack") or data.get("chk_heart") or data.get("heart_attack")
        )
        highchol = _coerce_bool_like(
            data.get("highchol") or data.get("chk_chol") or data.get("cholesterol")
        )
        diffwalk = _coerce_bool_like(
            data.get("diffwalk") or data.get("chk_walk") or data.get("walking_difficulty")
        )
        physactivity = _coerce_bool_like(
            data.get("physactivity") or data.get("chk_activity") or data.get("physical_activity")
        )
        alcohol = _coerce_bool_like(data.get("alcohol") or data.get("chk_alcohol"))
        smoking = _coerce_bool_like(data.get("smoking"))

        stress_raw = data.get("stress_level") or data.get("stress")
        stress_level = _map_stress_value(stress_raw)

        # Build the raw_input dictionary in the names expected by feature_encoder.encode_raw_input
        raw_input = {
            "gender": gender,
            "age": age,
            "height": height,
            "weight": weight,
            "systolic": systolic,
            "diastolic": diastolic,
            "sleeptime": sleeptime,  # canonical key used by encoder
            "chest_pain": chest_pain,
            "prior_heart_attack": prior_heart_attack,
            "highchol": highchol,
            "diffwalk": diffwalk,
            "physactivity": physactivity,
            "alcohol": alcohol,
            "smoking": smoking,
            "stress_level": stress_level,
        }

        logging.info(f"[manual-entry] normalized raw_input: {raw_input}")

        # Call Predictor for each disease
        diabetes_pred = predictor.predict("diabetes", raw_input)
        heart_pred = predictor.predict("heart", raw_input)
        stroke_pred = predictor.predict("stroke", raw_input)

        response = {
            "status": "success",
            "success": True,
            "input": raw_input,
            "predictions": {
                "diabetes": diabetes_pred,
                "heart": heart_pred,
                "stroke": stroke_pred,
            },
        }

        return jsonify(response)

    except Exception as e:
        logging.exception("Error in /manual-entry")
        return jsonify({"status": "error", "success": False, "error": str(e)}), 500
