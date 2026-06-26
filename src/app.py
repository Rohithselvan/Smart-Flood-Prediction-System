import sys
import os

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from src.predictor import FloodPredictor
from src.geo_fetcher import fetch_all

# ✅ Local model paths
MODEL_PATH = os.path.join(BASE_DIR, "models", "flood_predictor.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

# ✅ Templates & static folders
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

CORS(app)

# Load model
predictor = FloodPredictor(MODEL_PATH, SCALER_PATH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json()
        area = data.get("area", "").strip()

        if not area:
            return jsonify({"error": "Enter area"}), 400

        result = fetch_all(area)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        terrain = data["terrain"]
        forecast = data["forecast"]

        preds = predictor.predict_3days(terrain, forecast)

        return jsonify({"predictions": preds})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5011)