# machine_learning/prediction/utils.py
import numpy as np

def prob_to_percent(p: float) -> float:
    return float(round(p * 100, 2))

def percent_to_risk_label(pct: float) -> str:
    # simple buckets (tuneable)
    if pct < 20: return "Low"
    if pct < 50: return "Moderate"
    return "High"

def listify(x):
    return list(x) if hasattr(x, "__iter__") and not isinstance(x, str) else [x]
