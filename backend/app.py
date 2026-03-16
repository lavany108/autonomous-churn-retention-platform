from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model
model = pickle.load(open("models/churn_model.pkl", "rb"))

@app.route("/")
def home():
    return "Customer Churn Prediction API Running"

@app.route("/predict", methods=["POST"])
def predict():

    data = request.json
    features = data["features"]

    features = np.array(features).reshape(1, -1)

    prediction = model.predict(features)[0]

    if prediction == 1:
        result = "High Churn Risk"
    else:
        result = "Low Churn Risk"

    return jsonify({
        "prediction": result
    })

if __name__ == "__main__":
    app.run(debug=True)