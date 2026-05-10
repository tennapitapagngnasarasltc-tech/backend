import pandas as pd
import joblib

scaler  = joblib.load("app/model/scaler.pkl")
columns = joblib.load("app/model/columns.pkl")

def preprocess(data):
    df = pd.DataFrame([data.dict()])

    df["sleep_efficiency"] = df["sleep_duration"] / 8
    df["stress_activity_ratio"] = (
        df["stress_level"] / (df["physical_activity_level"] + 1))

    df = pd.get_dummies(df)

    for col in columns:
        if col not in df:
            df[col] = 0

    df = df[columns]
    return scaler.transform(df)