import pandas as pd
import joblib
import json
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.cluster import KMeans
from data_preprocessing import load_raw_data


MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
CLASSIFIER_MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
SEGMENTER_MODEL_PATH = os.path.join(MODEL_DIR, "customer_segmenter.pkl")
SEGMENT_METADATA_PATH = os.path.join(MODEL_DIR, "segment_metadata.json")


def train():
    df = load_raw_data("../../data/dataset.csv")

    X = df.drop("Churn", axis=1)
    y = df["Churn"].map({"No": 0, "Yes": 1})

    # Identify numeric and categorical columns
    numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
    categorical_features = [
        "gender",
        "SeniorCitizen",
        "Partner",
        "Dependents",
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
        "PaymentMethod"
    ]

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    # Create full pipeline
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000))
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    score = accuracy_score(y_test, preds)

    print("Pipeline Accuracy:", score)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, CLASSIFIER_MODEL_PATH)

    print("Pipeline model saved successfully!")

    train_segmentation_model(df)


def train_segmentation_model(df):
    segmentation_features = [
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
        "Contract",
        "InternetService",
        "PaymentMethod",
    ]

    numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
    categorical_features = ["Contract", "InternetService", "PaymentMethod"]

    X = df[segmentation_features].copy()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    segmenter = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("cluster", KMeans(n_clusters=4, random_state=42, n_init=10)),
        ]
    )

    segmenter.fit(X)
    clusters = segmenter.predict(X)

    labeled_df = X.copy()
    labeled_df["cluster"] = clusters

    profiles = {}
    grouped = labeled_df.groupby("cluster")
    for cluster_id, group in grouped:
        avg_tenure = float(group["tenure"].mean())
        avg_charges = float(group["MonthlyCharges"].mean())
        dominant_contract = group["Contract"].mode().iat[0]

        if avg_tenure < 12 and dominant_contract == "Month-to-month":
            name = "Early-Life Flexible"
            description = "Newer customers with flexible contracts; onboarding and first-year value communication is key."
        elif avg_charges >= 80:
            name = "High-Value Premium"
            description = "Higher monthly spend segment; prioritize premium support and proactive retention offers."
        elif avg_tenure >= 36:
            name = "Loyal Long-Term"
            description = "Long-tenure users with stable usage; maintain loyalty through benefits and periodic upgrades."
        else:
            name = "Value Seekers"
            description = "Moderate usage and pricing sensitivity; respond well to targeted pricing bundles."

        profiles[str(cluster_id)] = {
            "segment_name": name,
            "segment_description": description,
            "avg_tenure": round(avg_tenure, 2),
            "avg_monthly_charges": round(avg_charges, 2),
            "dominant_contract": dominant_contract,
            "size": int(len(group)),
        }

    joblib.dump(segmenter, SEGMENTER_MODEL_PATH)
    with open(SEGMENT_METADATA_PATH, "w", encoding="utf-8") as file_obj:
        json.dump(profiles, file_obj, indent=2)

    print("Segmentation model and metadata saved successfully!")


if __name__ == "__main__":
    train()