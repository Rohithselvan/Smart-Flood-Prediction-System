"""
predictor.py
Local version:
✔ Auto feature alignment
✔ Hybrid logic (rule + ML)
✔ Works with local project structure
"""

import numpy as np
import joblib #type: ignore
import os
import sys

# ─────────────────────────────────────────────
# PATH SETUP (LOCAL FIX)
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Import feature names
try:
    from src.feature_engineering import FEATURE_NAMES
except:
    FEATURE_NAMES = [
        "Slope", "Curvature", "Aspect",
        "TWI", "FA", "Drainage", "Rainfall"
    ]
    print("⚠️ Using default FEATURE_NAMES")


class FloodPredictor:
    def __init__(self, model_path, scaler_path):

        self.model  = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

        self.feature_names = FEATURE_NAMES

        print(f"✅ Model loaded: {model_path}")
        print(f"✅ Scaler loaded: {scaler_path}")
        print("📊 Features expected:", self.feature_names)

    # ─────────────────────────────────────────────
    # AUTO FEATURE ALIGNMENT
    # ─────────────────────────────────────────────
    def build_feature_vector(self, terrain, forecast_day):

        combined = {}

        # Terrain
        for k, v in terrain.items():
            combined[k.lower()] = v

        # Forecast
        for k, v in forecast_day.items():
            combined[k.lower()] = v

        features = []

        for name in self.feature_names:
            key = name.lower()

            if key in combined:
                features.append(float(combined[key]))

            elif "rain" in key:
                features.append(float(combined.get("total_mm", 0)))

            elif "hour" in key:
                features.append(float(combined.get("hours_rain", 0)))

            else:
                features.append(0.0)

        return np.array(features).reshape(1, -1)

    # ─────────────────────────────────────────────
    # SINGLE DAY PREDICTION
    # ─────────────────────────────────────────────
    def predict_day(self, terrain, forecast_day):

        terrain = terrain or {}
        forecast_day = forecast_day or {}

        rainfall = forecast_day.get("total_mm", 0)
        hours    = forecast_day.get("hours_rain", 0)
        peak     = forecast_day.get("max_hourly_mm", 0)

        # ── RULE-BASED SAFETY ──
        if rainfall == 0:
            return {
                "flood": False,
                "probability": 0.0,
                "risk_level": "Low",
                "color": "#66bb6a",
                "icon": "🟢"
            }

        # ── Base probability (rainfall logic) ──
        if rainfall < 5:
            base_prob = 0.1
        elif rainfall < 20:
            base_prob = 0.3
        elif rainfall < 50:
            base_prob = 0.6
        else:
            base_prob = 0.85

        # ── Build ML features ──
        X = self.build_feature_vector(terrain, forecast_day)

        print("🔍 Features:", X)

        # Scale
        X_scaled = self.scaler.transform(X)

        # ML probability
        model_prob = self.model.predict_proba(X_scaled)[0][1]

        # ── HYBRID LOGIC ──
        # (You temporarily replaced with rainfall logic — keeping your version)
        prob = rainfall / 100

        # ── INTENSITY BOOST ──
        if peak > 20:
            prob += 0.1

        if hours > 10:
            prob += 0.05

        # ── TERRAIN EFFECT ──
        slope = terrain.get("Slope", 0)
        if slope < 5:
            prob += 0.05

        prob = min(prob, 1.0)

        flood = prob >= 0.5

        # ── RISK LEVEL ──
        if prob >= 0.75:
            risk  = "Very High"
            color = "#ef5350"
            icon  = "🔴"
        elif prob >= 0.5:
            risk  = "High"
            color = "#ff7043"
            icon  = "🟠"
        elif prob >= 0.35:
            risk  = "Moderate"
            color = "#ffca28"
            icon  = "🟡"
        else:
            risk  = "Low"
            color = "#66bb6a"
            icon  = "🟢"

        return {
            "flood"      : bool(flood),
            "probability": round(float(prob) * 100, 1),
            "risk_level" : risk,
            "color"      : color,
            "icon"       : icon
        }

    # ─────────────────────────────────────────────
    # 3 DAY PREDICTION
    # ─────────────────────────────────────────────
    def predict_3days(self, terrain, forecast):

        results = []

        for day in forecast:
            pred = self.predict_day(terrain, day)

            pred.update({
                "date"          : day.get("date", "N/A"),
                "rainfall_mm"   : day.get("total_mm", 0),
                "max_hourly_mm" : day.get("max_hourly_mm", 0),
                "hours_rain"    : day.get("hours_rain", 0)
            })

            results.append(pred)

        return results