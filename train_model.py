import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import joblib

df = pd.read_csv("app/data/featured_sleep.csv")

y = df["quality_of_sleep"]
X = df.drop(columns=["quality_of_sleep"])
X = pd.get_dummies(X)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42)

model = XGBRegressor(
    n_estimators=300, learning_rate=0.05, max_depth=6)
model.fit(X_train, y_train)

joblib.dump(model,  "app/model/model.pkl")
joblib.dump(scaler, "app/model/scaler.pkl")
joblib.dump(X.columns.tolist(), "app/model/columns.pkl")
print("Model trained and saved")