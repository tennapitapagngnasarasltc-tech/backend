import pandas as pd

df = pd.read_csv("app/data/sleep_data.csv")

if "Person ID" in df.columns:
    df = df.drop(columns=["Person ID"])

df = df.dropna()

def parse_bp(x):
    try:
        s, d = x.split("/")
        return int(s), int(d)
    except:
        return None, None

if df["Blood Pressure"].dtype == object:
    df["Systolic"], df["Diastolic"] = zip(
        *df["Blood Pressure"].map(parse_bp))
    df = df.drop(columns=["Blood Pressure"])

df.columns = [c.strip().lower().replace(" ","_")
              for c in df.columns]

df.to_csv("app/data/clean_sleep.csv", index=False)
print("Clean dataset saved")