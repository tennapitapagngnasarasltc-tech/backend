import os

from supabase import create_client


SUGGESTION_FIELDS = "id,title,suggestion_note,score_band"
SCAN_BATCH_SIZE = 100


def _normalize_band(value: str | None) -> str:
    return value.strip().casefold() if isinstance(value, str) else ""


def _create_user_client(access_token: str):
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", "")
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be configured")

    client = create_client(supabase_url, supabase_key)
    client.postgrest.auth(access_token)
    return client


def _empty_response(status: str, message: str, score_band: str | None = None) -> dict:
    return {
        "status": status,
        "message": message,
        "score_band": score_band,
        "suggestions": [],
        "limit": 0,
        "offset": 0,
        "next_offset": None,
        "has_more": False,
    }


def get_user_suggestions(
    user_id: str,
    access_token: str,
    *,
    limit: int = 3,
    offset: int = 0,
    expected_score_band: str | None = None,
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
        return _empty_response(
            "no_prediction", "No sleep prediction found. Create one to get suggestions."
        )

    raw_band = predictions[0].get("score_band")
    normalized_band = _normalize_band(raw_band)
    if not normalized_band:
        return _empty_response(
            "no_score_band", "Your latest prediction does not have a score band."
        )

    score_band = raw_band.strip()
    if expected_score_band and (
        _normalize_band(expected_score_band) != normalized_band
    ):
        return _empty_response(
            "band_changed",
            "Your latest sleep score band changed. Refresh suggestions to continue.",
            score_band,
        )

    matching_suggestions = []
    scan_offset = 0
    needed_count = offset + limit + 1
    while len(matching_suggestions) < needed_count:
        response = (
            client.table("user_suggestions")
            .select(SUGGESTION_FIELDS)
            .ilike("score_band", f"%{score_band}%")
            .order("id", desc=False)
            .range(scan_offset, scan_offset + SCAN_BATCH_SIZE - 1)
            .execute()
        )
        rows = response.data or []
        matching_suggestions.extend(
            row
            for row in rows
            if _normalize_band(row.get("score_band")) == normalized_band
        )
        scan_offset += len(rows)
        if len(rows) < SCAN_BATCH_SIZE:
            break

    page = matching_suggestions[offset : offset + limit]
    has_more = len(matching_suggestions) > offset + limit
    if not page:
        return _empty_response(
            "no_matching_suggestions",
            f"No suggestions match the {score_band} sleep-quality band.",
            score_band,
        )

    return {
        "status": "ok",
        "message": "Suggestions found.",
        "score_band": score_band,
        "suggestions": page,
        "limit": limit,
        "offset": offset,
        "next_offset": offset + len(page) if has_more else None,
        "has_more": has_more,
    }
