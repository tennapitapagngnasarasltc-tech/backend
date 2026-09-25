import os

from supabase import create_client


ENTERTAINMENT_FIELDS = (
    "id,title,type,media_file_url,cover_img_url,sleep_quality,status"
)


def _normalized_band(value: str | None) -> str:
    return value.strip().casefold() if isinstance(value, str) else ""


def _create_user_client(access_token: str):
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", "")
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be configured")

    client = create_client(supabase_url, supabase_key)
    client.postgrest.auth(access_token)
    return client


def get_for_you_recommendations(
    user_id: str,
    access_token: str,
    client_factory=_create_user_client,
) -> dict:
    client = client_factory(access_token)
    latest_prediction = (
        client.table("predictions")
        .select("score_band")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    predictions = latest_prediction.data or []

    if not predictions:
        return {
            "status": "empty",
            "message": "No prediction found. Create a sleep prediction first.",
            "score_band": None,
            "recommendations": [],
        }

    score_band = predictions[0].get("score_band")
    normalized_score_band = _normalized_band(score_band)
    if not normalized_score_band:
        return {
            "status": "empty",
            "message": "Your latest prediction has no score band yet.",
            "score_band": None,
            "recommendations": [],
        }

    active_content = (
        client.table("entertainments")
        .select(ENTERTAINMENT_FIELDS)
        .eq("status", "active")
        .execute()
    )
    recommendations = [
        item
        for item in (active_content.data or [])
        if _normalized_band(item.get("sleep_quality")) == normalized_score_band
    ]

    return {
        "status": "ok" if recommendations else "empty",
        "message": (
            "Recommendations found."
            if recommendations
            else f"No active entertainment found for the {score_band} sleep-quality band."
        ),
        "score_band": score_band,
        "recommendations": recommendations,
    }
