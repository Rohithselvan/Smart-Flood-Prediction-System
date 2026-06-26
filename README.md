<img width="1535" height="1024" alt="Image" src="https://github.com/user-attachments/assets/abd1142a-dffb-4837-b4e8-140f15e05f9e" />

## 📚 Table of Contents

- [✨ Features](#-features)
- [⚙️ How It Works](#️-how-it-works)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [📓 Notebooks](#-notebooks)
- [🚀 Installation](#-installation)
- [🏋️ Training the Model](#️-training-the-model)
- [▶️ Running the Application](#️-running-the-application)
- [📸 Demo](#-demo)
- [📈 Results](#-results)
- [🚀 Future Improvements](#-future-improvements)
- [📄 License](#-license)

---

## ✨ Features

* 🌍 Search any location using OpenStreetMap
* 🗺️ Interactive map visualization with Leaflet
* 🌦️ Real-time weather forecast integration
* 🛰️ Automatic terrain feature extraction
* 🤖 Ensemble Machine Learning (Random Forest + Gradient Boosting)
* 📊 Flood probability prediction for the next 3 days
* ⚠️ Risk classification (Low, Moderate, High)
* 💻 Responsive and interactive web interface

---

## ⚙️ How It Works

```text
User enters a location
          │
          ▼
OpenStreetMap Geocoding
          │
          ▼
Fetch Weather Forecast
          │
          ▼
Generate Terrain Features
          │
          ▼
Machine Learning Prediction
          │
          ▼
3-Day Flood Risk Forecast
```

---

## 🛠️ Tech Stack

* Python
* Flask
* Scikit-learn
* Pandas
* NumPy
* Joblib
* HTML
* CSS
* JavaScript
* Leaflet.js
* OpenStreetMap API
* Open-Meteo API

---

## 📁 Project Structure

```text
FLOOD_PREDICTION_PROJECT/
│
├── data/
│   └── india_flood_merged_final.csv
│
├── models/
│   ├── flood_predictor.pkl
│   └── scaler.pkl
│
├── notebooks/
│   ├── Training.ipynb
│   └── Testing.ipynb
│
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── feature_engineering.py
│   ├── geo_fetcher.py
│   ├── predictor.py
│   └── train_model.py
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── README.md
└── requirements.txt
```

---

## 📓 Notebooks

The `notebooks/` directory contains the original Jupyter notebooks used during the development of this project.

* **Training.ipynb** – Model development, feature engineering, and training.
* **Testing.ipynb** – Prediction experiments and model evaluation.

These notebooks are included for **reproducibility**, **experimentation**, and to document the model development process.

The production-ready implementation used by the web application is available in the `src/` directory.

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/Flood_Prediction_Project.git

cd Flood_Prediction_Project
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.\.venv\Scripts\Activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🏋️ Training the Model

If you want to train the model from scratch, place the dataset inside the `data/` directory and run:

```bash
python src/train_model.py
```

This generates:

```text
models/
├── flood_predictor.pkl
└── scaler.pkl
```

---

## ▶️ Running the Application

After the model has been trained (or the pre-trained model is available), start the Flask application:

```bash
python src/app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## 📸 Demo

### 🌆 Chennai — Low Flood Risk

> Displays terrain analysis, weather conditions, and a 3-day flood forecast for Chennai.

<img width="505" height="938" alt="Image" src="https://github.com/user-attachments/assets/5480cb9d-25e3-40b3-b5ef-30ee545923ce" />

---

### ⛰️ Munnar — Mountain Terrain

> Demonstrates prediction for a high-elevation region with different terrain characteristics.

<img width="510" height="944" alt="Image" src="https://github.com/user-attachments/assets/90c92fc2-3f04-4a09-964e-bd47adf1ac94" />

---

### 🌧️ Goa — Moderate Flood Risk

> Example showing increased flood probability due to weather and terrain conditions.

<img width="499" height="939" alt="Image" src="https://github.com/user-attachments/assets/2e81ecc8-db9e-44b8-a2f1-27772fb938b6" />

---

# 📊 Results

The Smart Flood Prediction System combines geospatial analysis, real-time weather forecasting, and machine learning to estimate flood risk for the next three days based on a user-selected location.

### Key Outcomes

- 🌍 Predicts flood risk using only a **location name** as input
- 🛰️ Automatically retrieves geographical coordinates using **OpenStreetMap**
- ⛰️ Extracts terrain and elevation information using public APIs
- 🌧️ Fetches real-time weather data for flood risk assessment
- 🤖 Uses an ensemble of **Random Forest** and **Gradient Boosting** models for prediction
- 📅 Generates flood probability forecasts for the next **3 days**
- ⚠️ Classifies flood risk into **Low**, **Moderate**, and **High** categories
- 🗺️ Displays an interactive map along with prediction results
- 💻 Provides a responsive and user-friendly web interface
- 📓 Includes Jupyter notebooks for **reproducibility** and **experimentation**, while the `src/` directory contains the production-ready implementation

---

### Highlights

| Capability | Status |
|------------|:------:|
| Location Search | ✅ |
| Terrain Feature Extraction | ✅ |
| Weather Forecast Integration | ✅ |
| Ensemble Machine Learning | ✅ |
| 3-Day Flood Prediction | ✅ |
| Interactive Map | ✅ |
| Responsive Web Interface | ✅ |
| Training Notebook | ✅ |
| Testing Notebook | ✅ |

---

## 🚀 Future Improvements

* Satellite imagery integration
* River water level monitoring
* Deep learning-based prediction models
* Live rainfall radar visualization
* Mobile application support
* SMS/Email flood alerts

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

**Developed by Rohith**

If you found this project useful, consider giving it a ⭐ on GitHub.

</div>
