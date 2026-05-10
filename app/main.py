import uuid
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.sleep import SleepInput
from app.utils.preprocess import preprocess
from app.model.predictor import predict
from app.services.strategy import generate_strategy
from app.services.profile_service import save_profile, save_prediction, get_profile
from app.auth import get_current_user

app = FastAPI(title="Nidra API")

# ── CORS ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health check ─────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Nidra running"}

# ── Predict (Protected) ──────────────────────────────
@app.post("/predict")
def predict_sleep(
    data: SleepInput,
    user=Depends(get_current_user)
):
    user_id = user.id
    user_email = user.email

    # 1. ML prediction
    features = preprocess(data)
    raw_score = predict(features)
    score = float(raw_score)   # ✅ FIX

    # 2. Score band
    if score < 5:
        band = "Critical"
    elif score < 6:
        band = "Poor"
    elif score < 7:
        band = "Fair"
    elif score < 8:
        band = "Good"
    else:
        band = "Excellent"

    # 3. Strategy
    result = generate_strategy(score, data)

    # 4. Calculate sleep metrics automatically
    # Sleep quality: derived from prediction score (0-10 scale)
    calculated_sleep_quality = min(10, max(1, round(score)))
    
    # Deep sleep percentage: typically 13-23% based on sleep duration
    # Higher sleep_duration correlates with better deep sleep
    calculated_deep_sleep_pct = min(25, 13 + (data.sleep_duration / 8) * 10)
    
    # REM sleep percentage: typically 20-25% based on sleep duration
    calculated_rem_sleep_pct = min(30, 20 + (data.sleep_duration / 8) * 5)
    
    # Sleep efficiency: percentage of target sleep achieved (8 hours = 100%)
    calculated_sleep_percent = min(100, round((data.sleep_duration / 8) * 100))
    
    # Update data object with calculated metrics (only if not already provided)
    if data.sleep_quality is None:
        data.sleep_quality = calculated_sleep_quality
    if data.deep_sleep_pct is None:
        data.deep_sleep_pct = round(calculated_deep_sleep_pct, 2)
    if data.rem_sleep_pct is None:
        data.rem_sleep_pct = round(calculated_rem_sleep_pct, 2)
    if data.sleep_percent is None:
        data.sleep_percent = calculated_sleep_percent

    # 5. Save profile with prediction metadata
    try:
        save_profile(user_id, user_email, data, round(score, 2), band)
        print(f"[Supabase] Profile saved → {user_email}")
    except Exception as e:
        print(f"[Supabase ERROR]: {e}")

    # 6. Save prediction
    prediction_data = {
        "sleep_score": round(score, 2),
        "score_band": band,
        "overall": result["overall"],
        "priority_fixes": result["priority_fixes"],
        "strategies": result["strategies"],
        "warnings": result["warnings"],
        "positives": result["positives"],
    }
    
    # Sleep metrics to save
    sleep_metrics = {
        "sleep_quality": data.sleep_quality,
        "deep_sleep_pct": data.deep_sleep_pct,
        "rem_sleep_pct": data.rem_sleep_pct,
        "sleep_percent": data.sleep_percent,
    }
    
    try:
        save_prediction(user_id, prediction_data, sleep_metrics)
        print(f"[Supabase] Prediction saved → {user_email}")
    except Exception as e:
        print(f"[Supabase ERROR]: {e}")

    # 6. Response
    return {
        "user_id": user_id,
        "email": user_email,
        "sleep_score": round(score, 2),
        "score_band": band,
        "sleep_quality": data.sleep_quality,
        "deep_sleep_pct": data.deep_sleep_pct,
        "rem_sleep_pct": data.rem_sleep_pct,
        "sleep_percent": data.sleep_percent,
        "overall": result["overall"],
        "priority_fixes": result["priority_fixes"],
        "strategies": result["strategies"],
        "warnings": result["warnings"],
        "positives": result["positives"],
    }

# ── Get Profile ──────────────────────────────────────
@app.get("/profile")
def get_my_profile(user=Depends(get_current_user)):
    profile = get_profile(user.id)
    if not profile:
        return {"message": "No profile saved yet. Call /predict first."}
    return profile