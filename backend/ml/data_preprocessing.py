import pandas as pd
from sklearn.model_selection import train_test_split

def load_raw_data(path):
    df = pd.read_csv(path)

    # Fix TotalCharges column
    df["TotalCharges"] = df["TotalCharges"].replace(" ", None)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Drop missing rows
    df = df.dropna()

    # Drop customerID if present
    if "customerID" in df.columns:
        df = df.drop("customerID", axis=1)

    return df