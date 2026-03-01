import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def load_and_preprocess_data(path):
    df = pd.read_csv(path)

    # Drop customerID column
    if 'customerID' in df.columns:
        df.drop('customerID', axis=1, inplace=True)

    # Convert TotalCharges to numeric
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

    # Handle missing values
    df.fillna(df.median(numeric_only=True), inplace=True)

    # Encode categorical variables
    label_encoders = {}
    for column in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le

    # Separate features and target
    X = df.drop('Churn', axis=1)
    y = df['Churn']

    return train_test_split(X, y, test_size=0.2, random_state=42)