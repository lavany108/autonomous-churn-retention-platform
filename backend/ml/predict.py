import joblib
import numpy as np
import os
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "churn_model.pkl")

model = joblib.load(MODEL_PATH)

EXPECTED_FEATURES = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]


def get_risk_segmentation(probability):
    if probability >= 0.80:
        return "Critical", "Immediate retention call + 30% discount + manager escalation"
    if probability >= 0.60:
        return "High", "Retention call + targeted offer"
    if probability >= 0.40:
        return "Medium", "Personalized engagement email + loyalty benefits"
    if probability >= 0.20:
        return "Low", "Automated check-in email"
    return "Very Low", "No action required"


def predict_from_payload(payload):
    missing = [feature for feature in EXPECTED_FEATURES if feature not in payload]
    if missing:
        raise ValueError(f"Missing required features: {', '.join(missing)}")

    input_df = pd.DataFrame([{feature: payload[feature] for feature in EXPECTED_FEATURES}])

    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])
    risk_tier, action = get_risk_segmentation(probability)

    return {
        "churn_prediction": prediction,
        "churn_probability": probability,
        "risk_tier": risk_tier,
        "recommended_action": action,
    }

def predict_churn(data):
    arr = np.array(data).reshape(1, -1)
    return int(model.predict(arr)[0])