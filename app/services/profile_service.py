from app.services.supabase_client import supabase, supabase_admin


# ───────────────────────────────────────────────
# SAVE / UPDATE PROFILE
# ───────────────────────────────────────────────
def save_profile(user_id: str, email: str, data, latest_score: float | None = None, score_band: str | None = None) -> dict:
    """
    Upsert user profile into Supabase using user_id as conflict key.
    Uses service role key to bypass RLS (backend operation).

    WHY user_id instead of id:
    - "id" is auto-generated (new UUID each time) → would create duplicate rows
    - "user_id" is UNIQUE → matches same user across multiple predictions → updates existing row
    """

    profile_data = {
        "user_id": user_id,
        "user_email": email,
        "gender": data.gender,
        "age": data.age,
        "occupation": data.occupation,
        "sleep_duration": data.sleep_duration,
        "physical_activity_level": data.physical_activity_level,
        "stress_level": data.stress_level,
        "bmi_category": data.bmi_category,
        "systolic": data.systolic,
        "diastolic": data.diastolic,
        "latest_score": latest_score,
        "score_band": score_band,
        # Sleep tracking metrics (optional)
        "sleep_quality": data.sleep_quality,
        "deep_sleep_pct": data.deep_sleep_pct,
        "rem_sleep_pct": data.rem_sleep_pct,
        "sleep_percent": data.sleep_percent,
    }

    # Remove None values to prevent overwriting existing data with NULL
    profile_data = {k: v for k, v in profile_data.items() if v is not None}

    print(f"\n[DEBUG] save_profile called:")
    print(f"  user_id={user_id}, email={email}")
    print(f"  latest_score={latest_score}, score_band={score_band}")
    print(f"  sleep_quality={data.sleep_quality}, deep_sleep_pct={data.deep_sleep_pct}")
    print(f"  rem_sleep_pct={data.rem_sleep_pct}, sleep_percent={data.sleep_percent}")
    print(f"  Sending to Supabase: {profile_data}")

    try:
        response = (
            supabase_admin
            .table("profiles")
            .insert(profile_data, on_conflict="user_id")
            .select("*")
            .execute()
        )

        print(f"[DEBUG] Response object: {response}")
        print(f"[DEBUG] Response data: {response.data if hasattr(response, 'data') else 'N/A'}")
        print(f"[DEBUG] Response error: {response.error if hasattr(response, 'error') else 'N/A'}")

        if getattr(response, 'error', None) is not None:
            print(f"❌ [Supabase ERROR] Failed to upsert profile for {email}: {response.error}")
            return {}

        if response.data and len(response.data) > 0:
            saved_profile = response.data[0]
            print(f"✅ [Supabase] Profile upserted for {email}")
            print(f"   User ID: {saved_profile.get('user_id')}")
            print(f"   Score: {saved_profile.get('latest_score')} ({saved_profile.get('score_band')})")
            return saved_profile
        else:
            print(f"❌ [Supabase] No data returned from upsert for {email}")
            return {}

    except Exception as e:
        print(f"❌ [Supabase ERROR] Failed to upsert profile for {email}")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


# ───────────────────────────────────────────────
# SAVE PREDICTION
# ───────────────────────────────────────────────
def save_prediction(user_id: str, prediction_data: dict, sleep_metrics: dict | None = None) -> dict:
    """
    Insert prediction data into Supabase predictions table.
    Also includes sleep metrics (quality, deep sleep %, REM %, sleep %).
    """
    pred_data = {
        "user_id": user_id,
        "sleep_score": prediction_data["sleep_score"],
        "score_band": prediction_data["score_band"],
        "overall": prediction_data["overall"],
        "priority_fixes": prediction_data["priority_fixes"],
        "strategies": prediction_data["strategies"],
        "warnings": prediction_data["warnings"],
        "positives": prediction_data["positives"],
    }
    
    # Add sleep metrics if provided
    if sleep_metrics:
        pred_data["sleep_quality"] = sleep_metrics.get("sleep_quality")
        pred_data["deep_sleep_pct"] = sleep_metrics.get("deep_sleep_pct")
        pred_data["rem_sleep_pct"] = sleep_metrics.get("rem_sleep_pct")
        pred_data["sleep_percent"] = sleep_metrics.get("sleep_percent")

    print(f"\n[DEBUG] save_prediction called:")
    print(f"  user_id={user_id}")
    print(f"  sleep_quality={pred_data.get('sleep_quality')}")
    print(f"  deep_sleep_pct={pred_data.get('deep_sleep_pct')}")
    print(f"  rem_sleep_pct={pred_data.get('rem_sleep_pct')}")
    print(f"  sleep_percent={pred_data.get('sleep_percent')}")
    print(f"  Sending to Supabase: {pred_data}")

    try:
        response = (
            supabase_admin
            .table("predictions")
            .insert(pred_data)
            .select("*")
            .execute()
        )

        if getattr(response, 'error', None) is not None:
            print(f"❌ [Supabase ERROR] Failed to save prediction for {user_id}: {response.error}")
            return {}

        if response.data and len(response.data) > 0:
            saved_pred = response.data[0]
            print(f"✅ [Supabase] Prediction saved for {user_id}")
            print(f"   Sleep Score: {saved_pred.get('sleep_score')} ({saved_pred.get('score_band')})")
            print(f"   Sleep Quality: {saved_pred.get('sleep_quality')}")
            print(f"   Deep Sleep: {saved_pred.get('deep_sleep_pct')}%")
            print(f"   REM Sleep: {saved_pred.get('rem_sleep_pct')}%")
            return saved_pred
        else:
            print(f"❌ [Supabase] No data returned from prediction save for {user_id}")
            return {}

    except Exception as e:
        print(f"❌ [Supabase ERROR] Failed to save prediction for {user_id}")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


# ───────────────────────────────────────────────
# GET PROFILE
# ───────────────────────────────────────────────
def get_profile(user_id: str) -> dict | None:
    """
    Fetch user profile from Supabase by user_id.
    Uses service role key for backend read (bypass RLS).
    Returns None if profile not found.
    """
    try:
        # Use SERVICE ROLE client to bypass RLS
        response = (
            supabase_admin
            .table("profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if response.data and len(response.data) > 0:
            profile = response.data[0]
            print(f"✅ [Supabase] Profile retrieved for user {user_id}")
            return profile
        else:
            print(f"ℹ️  [Supabase] No profile found for user {user_id}")
            return None

    except Exception as e:
        print(f"❌ [Supabase ERROR] Failed to get profile for {user_id}")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None