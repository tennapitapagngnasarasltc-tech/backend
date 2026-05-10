from pydantic import BaseModel
from typing import Optional


class SleepInput(BaseModel):
    # Profile fields
    gender:                  str
    age:                     int
    occupation:              str
    sleep_duration:          float
    physical_activity_level: int
    stress_level:            int
    bmi_category:            str
    systolic:                int
    diastolic:               int

    # Optional sleep tracking metrics
    sleep_quality: Optional[int] = None          # 1-10 scale
    deep_sleep_pct: Optional[float] = None       # percentage 0-100
    rem_sleep_pct: Optional[float] = None        # percentage 0-100
    sleep_percent: Optional[float] = None        # percentage 0-100

    # Optional — pass this from Flutter once you add Supabase Auth
    # For now you can send any unique string (e.g. "test-user-001")
    user_id: Optional[str] = None