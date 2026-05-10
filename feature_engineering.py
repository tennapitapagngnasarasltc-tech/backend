import pandas as pd

df = pd.read_csv("app/data/clean_sleep.csv")

df["sleep_efficiency"] = df["sleep_duration"] / 8
df["stress_activity_ratio"] = (
    df["stress_level"] / (df["physical_activity_level"] + 1))

df.to_csv("app/data/featured_sleep.csv", index=False)
print("Feature engineered dataset saved")