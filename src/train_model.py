# ============================================================
# INDIA FLOOD PREDICTION — LOCAL TRAINING SCRIPT
# ============================================================

import os
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils import resample
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PATH SETUP (IMPORTANT)
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "india_flood_merged_final.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "flood_predictor.pkl")

# ─────────────────────────────────────────────
# STEP 1: Load Dataset
# ─────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
print("✅ Dataset loaded. Shape:", df.shape)

# ─────────────────────────────────────────────
# STEP 2: Drop Unnecessary / Leaky Columns
# ─────────────────────────────────────────────
df.drop(columns=[
    'avg_severity',
    'Event_x_Severity',
    'Rainfall_Anomaly_Z',
    'Rainfall_x_Anomaly',
    'Anomaly_Squared'
], inplace=True, errors='ignore')

# ─────────────────────────────────────────────
# STEP 3: Fill Missing Values
# ─────────────────────────────────────────────
for col in [
    'ANNUAL',
    'Rolling_3yr_Annual',
    'Annual_x_Monsoon',
    'Monsoon_to_Annual_Ratio'
]:
    if col in df.columns:
        df[col].fillna(df[col].median(), inplace=True)

# ─────────────────────────────────────────────
# STEP 4: Feature Selection
# ─────────────────────────────────────────────
features = [
    'ANNUAL',
    'Monsoon_Rainfall',
    'Rolling_3yr_Annual',
    'flood_event_count',
    'avg_duration_days',
    'avg_fatalities',
    'dominant_cause_encoded',
    'Duration_x_Fatality',
    'Monsoon_to_Annual_Ratio',
]

X = df[features].fillna(0)
y = df['Flood_Label']

print("\n📊 Class Distribution:")
print(y.value_counts())

# ─────────────────────────────────────────────
# STEP 5: Time-Based Split
# ─────────────────────────────────────────────
df_sorted = df.sort_values('YEAR').reset_index(drop=True)
split_idx = int(len(df_sorted) * 0.80)

train_df = df_sorted.iloc[:split_idx]
test_df  = df_sorted.iloc[split_idx:]

X_train = train_df[features].fillna(0)
y_train = train_df['Flood_Label']
X_test  = test_df[features].fillna(0)
y_test  = test_df['Flood_Label']

print(f"\n✅ Train size: {len(X_train)} | Test size: {len(X_test)}")

# ─────────────────────────────────────────────
# STEP 6: Handle Imbalance (Partial Oversampling)
# ─────────────────────────────────────────────
train_combined = pd.concat([X_train, y_train], axis=1)

majority = train_combined[train_combined['Flood_Label'] == 0]
minority = train_combined[train_combined['Flood_Label'] == 1]

minority_up = resample(
    minority,
    replace=True,
    n_samples=int(len(majority) * 0.4),
    random_state=42
)

train_bal = pd.concat([majority, minority_up]).sample(frac=1, random_state=42)

X_train_bal = train_bal[features]
y_train_bal = train_bal['Flood_Label']

# ─────────────────────────────────────────────
# STEP 7: Train Random Forest
# ─────────────────────────────────────────────
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=6,
    min_samples_leaf=10,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42
)

rf.fit(X_train_bal, y_train_bal)
rf_pred = rf.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)

print(f"\n✅ Random Forest Accuracy : {rf_acc * 100:.2f}%")
print(classification_report(y_test, rf_pred))

# ─────────────────────────────────────────────
# STEP 8: Train Gradient Boosting
# ─────────────────────────────────────────────
gb = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    min_samples_leaf=10,
    random_state=42
)

gb.fit(X_train_bal, y_train_bal)
gb_pred = gb.predict(X_test)
gb_acc = accuracy_score(y_test, gb_pred)

print(f"✅ Gradient Boosting Accuracy : {gb_acc * 100:.2f}%")
print(classification_report(y_test, gb_pred))

# ─────────────────────────────────────────────
# STEP 9: Select Best Model
# ─────────────────────────────────────────────
best_model = rf if rf_acc >= gb_acc else gb
best_name = "Random Forest" if rf_acc >= gb_acc else "Gradient Boosting"

print(f"\n🏆 Best Model: {best_name}")

# ─────────────────────────────────────────────
# STEP 10: Save Model
# ─────────────────────────────────────────────
os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(best_model, f)

print(f"✅ Model saved at: {MODEL_PATH}")