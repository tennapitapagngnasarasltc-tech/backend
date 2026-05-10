import joblib

model = joblib.load("app/model/model.pkl")

def predict(features):
    return model.predict(features)[0]