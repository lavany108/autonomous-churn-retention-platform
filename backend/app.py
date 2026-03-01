from flask import Flask, request, jsonify
import joblib
import os
import numpy as np
import pandas as pd

app = Flask(__name__)

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

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Convert JSON to DataFrame
    input_df = pd.DataFrame([data])
    
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    return jsonify({
    "churn_prediction": int(prediction),
    "churn_probability": float(probability)})


if __name__ == "__main__":
    app.run(debug=True)