FEATURE_NAMES = [
    "Slope",
    "Curvature",
    "Aspect",
    "TWI",
    "FA",
    "Drainage",
    "Rainfall"
]

def build_features(terrain, forecast_day):
    """
    Converts terrain + forecast → feature dictionary
    (Used if you want manual control instead of auto-mapping)
    """

    rainfall = forecast_day.get("total_mm", 0)

    features = {
        "Slope": terrain.get("Slope", 0),
        "Curvature": terrain.get("Curvature", 0),
        "Aspect": terrain.get("Aspect", 0),
        "TWI": terrain.get("TWI", 0),
        "FA": terrain.get("FA", 0),
        "Drainage": terrain.get("Drainage", 0),
        "Rainfall": rainfall
    }

    return features

def validate_features(feature_dict):
    """
    Ensures all required features exist
    """

    missing = []

    for f in FEATURE_NAMES:
        if f not in feature_dict:
            missing.append(f)

    if missing:
        print(f"⚠️ Missing features: {missing}")

    return True