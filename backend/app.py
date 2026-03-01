from flask import Flask, request, jsonify
import joblib
import os
import numpy as np
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load model once when server starts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../"))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "churn_model.pkl")

model = joblib.load(MODEL_PATH)


@app.route("/")
def home():
    return jsonify({"message": "Churn Prediction API running 🏃‍♀️"})


# @app.route("/predict", methods=["POST"])
# def predict():

#     data = request.json

#     # Convert JSON input into numpy array
#     features = np.array([list(data.values())])

#     prediction = model.predict(features)[0]
#     probability = model.predict_proba(features)[0][1]

#     return jsonify({
#         "churn_prediction": int(prediction),
#         "churn_probability": float(probability)
#     })

EXPECTED_FEATURES = [
    'gender',
    'SeniorCitizen',
    'Partner',
    'Dependents',
    'tenure',
    'PhoneService',
    'MultipleLines',
    'InternetService',
    'OnlineSecurity',
    'OnlineBackup',
    'DeviceProtection',
    'TechSupport',
    'StreamingTV',
    'StreamingMovies',
    'Contract',
    'PaperlessBilling',
    'PaymentMethod',
    'MonthlyCharges',
    'TotalCharges'
]

def get_risk_segmentation(probability):
    if probability >= 0.80:
        return "Critical", "Immediate retention call + 30% discount + manager escalation"
    elif probability >= 0.60:
        return "High", "Retention call + targeted offer"
    elif probability >= 0.40:
        return "Medium", "Personalized engagement email + loyalty benefits"
    elif probability >= 0.20:
        return "Low", "Automated check-in email"
    else:
        return "Very Low", "No action required"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Convert JSON to DataFrame
    input_df = pd.DataFrame([data])

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]
    risk_tier, action = get_risk_segmentation(probability)
    return jsonify({
    "churn_prediction": int(prediction),
    "churn_probability": float(probability),
    "risk_tier": risk_tier,
    "recommended_action": action})

if __name__ == "__main__":
    app.run(debug=True)