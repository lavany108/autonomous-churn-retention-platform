from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import joblib

from data_preprocessing import load_and_preprocess_data

def train():
    X_train, X_test, y_train, y_test = load_and_preprocess_data(
        "../../data/telecom_churn.csv"
    )

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "RandomForest": RandomForestClassifier(),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    }

    best_model = None
    best_score = 0

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        score = accuracy_score(y_test, preds)
        print(f"{name} Accuracy: {score}")

        if score > best_score:
            best_score = score
            best_model = model

    joblib.dump(best_model, "/Users/lavanyasmacbookair/Documents/T69/autonomous-churn-retention-platform/models/churn_model.pkl")
    print("Best model saved successfully!")

    print("Feature order used in training:")
    print(X_train.columns.tolist())

if __name__ == "__main__":
    train()