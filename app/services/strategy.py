def generate_strategy(score: float, data) -> dict:
    """
    Data-driven strategy engine built from actual dataset analysis.

    Score bands (from dataset quality_of_sleep distribution):
      Critical  : score < 5     (dataset min = 4)
      Poor      : 5 <= score < 6
      Fair      : 6 <= score < 7
      Good      : 7 <= score < 8
      Excellent : score >= 8    (dataset max = 9)
    """

    strategies = []
    priority   = []   # urgent / top fixes
    warnings   = []   # health flags
    positives  = []   # what they're doing right

    # ── helpers ──────────────────────────────────────────────────────────────
    sl  = data.stress_level
    sd  = data.sleep_duration
    pa  = data.physical_activity_level
    bmi = data.bmi_category.lower()
    sys = data.systolic
    dia = data.diastolic
    occ = data.occupation


    # ════════════════════════════════════════════════════════════════════════
    # 1. SLEEP DURATION
    #    Dataset shows clear score jumps:
    #    5–6h → avg 5.5 | 6–6.5h → 6.1 | 6.5–7h → 6.8 | 7–7.5h → 7.5 | 7.5h+ → 8.8
    # ════════════════════════════════════════════════════════════════════════
    if sd < 6.0:
        priority.append(
            "🚨 Critical: You slept under 6 hours. "
            "Dataset shows this drops your sleep quality score to ~5.5 on average. "
            "Target at least 7–7.5 hours — that range shows an avg score of 7.5."
        )
    elif sd < 6.5:
        strategies.append(
            "⏰ Sleep duration (6–6.5h) is below optimal. "
            "Try sleeping 30 min earlier each night this week to reach 7h+."
        )
    elif sd < 7.0:
        strategies.append(
            "🕐 You're close — push sleep duration from 6.5–7h to 7–7.5h "
            "for a meaningful quality boost (avg score jumps from 6.8 → 7.5)."
        )
    elif sd >= 7.5:
        positives.append("✅ Sleep duration is excellent (7.5h+) — this is your strongest asset.")


    # ════════════════════════════════════════════════════════════════════════
    # 2. STRESS LEVEL
    #    Dataset: stress 3 → avg quality 9.0 | stress 7 → 6.0 | stress 8 → 5.73
    # ════════════════════════════════════════════════════════════════════════
    if sl == 8:
        priority.append(
            "🚨 Critical: Stress level 8 is the highest in the dataset. "
            "People at this level average a sleep quality of only 5.7. "
            "Prioritise stress reduction: box breathing (4-7-8), 10 min wind-down, "
            "no screens 30 min before bed."
        )
    elif sl == 7:
        strategies.append(
            "😟 Stress level 7 pulls your sleep quality down to ~6.0 on average. "
            "Try a 10-minute guided meditation or journaling before bed to offload mental load."
        )
    elif sl >= 5:
        strategies.append(
            "😐 Moderate stress (level 5–6). Consider a consistent bedtime ritual "
            "to signal your body it's time to sleep — same time every night."
        )
    elif sl <= 4:
        positives.append(
            f"✅ Low stress (level {sl}) — this is a strong sleep quality driver. Keep it up."
        )


    # ════════════════════════════════════════════════════════════════════════
    # 3. PHYSICAL ACTIVITY
    #    Dataset sweet spot: 60–75 min/day → avg quality 8.82
    #    < 45 min → 6.22 | 45–60 → 7.67 | 75+ min → drops to 6.39 (overtraining)
    # ════════════════════════════════════════════════════════════════════════
    if pa < 45:
        strategies.append(
            f"🏃 Activity level ({pa} min/day) is below the dataset sweet spot. "
            "People doing 60–75 min/day score an avg sleep quality of 8.8. "
            "Add a 20-minute brisk walk daily to start."
        )
    elif 45 <= pa < 60:
        strategies.append(
            f"🏃 Good activity ({pa} min/day) — increase slightly to 60–75 min/day "
            "to reach the highest sleep quality zone in the dataset (avg 8.8)."
        )
    elif 60 <= pa <= 75:
        positives.append(
            f"✅ Activity level ({pa} min/day) is in the optimal zone (60–75 min). "
            "This is the #1 predictor of high sleep quality in your dataset."
        )
    elif pa > 75:
        warnings.append(
            f"⚠️ High activity ({pa} min/day) — dataset shows scores drop at 75+ min. "
            "Intense late-day exercise raises cortisol. Try finishing workouts 3h before bed."
        )


    # ════════════════════════════════════════════════════════════════════════
    # 4. BMI CATEGORY
    #    Dataset: Normal → 7.67 | Overweight → 6.89 | Obese → 6.40 | Normal Weight → 5.0
    # ════════════════════════════════════════════════════════════════════════
    if "obese" in bmi:
        warnings.append(
            "⚠️ Obese BMI category shows an avg sleep quality of 6.4 in the dataset. "
            "Weight management (even 5–10% reduction) significantly improves sleep depth and reduces apnea risk."
        )
    elif "overweight" in bmi:
        strategies.append(
            "📊 Overweight BMI averages 6.89 sleep quality vs 7.67 for Normal BMI. "
            "Combining 60–75 min activity with a balanced diet can shift both your weight and sleep score."
        )
    elif "normal" in bmi:
        positives.append("✅ Normal BMI — good foundation for high sleep quality.")


    # ════════════════════════════════════════════════════════════════════════
    # 5. BLOOD PRESSURE
    #    Dataset shows normal BP (<120) averages 7.25 quality
    #    Elevated (120–130) drops to 6.35
    # ════════════════════════════════════════════════════════════════════════
    if sys >= 140 or dia >= 90:
        warnings.append(
            f"🚨 Blood pressure {sys}/{dia} is in hypertension range. "
            "High BP disrupts deep sleep cycles. Reduce sodium, limit alcohol, "
            "and consult a doctor if this is persistent."
        )
    elif sys >= 130 or dia >= 85:
        warnings.append(
            f"⚠️ Blood pressure {sys}/{dia} is elevated. "
            "Elevated BP (120–130 systolic) is linked to avg sleep quality of 6.35 vs 7.25 for normal. "
            "Aim for regular aerobic activity to naturally lower it."
        )
    elif sys < 120 and dia < 80:
        positives.append(f"✅ Blood pressure {sys}/{dia} is normal — no sleep disruption from BP.")


    # ════════════════════════════════════════════════════════════════════════
    # 6. OCCUPATION-BASED INSIGHT
    #    Dataset avg quality: Scientist/Sales Rep/Software Eng → 4.0 | Nurse/Engineer/Lawyer → 7.5+
    # ════════════════════════════════════════════════════════════════════════
    high_stress_jobs = ["scientist", "sales representative", "software engineer", "salesperson"]
    if any(h in occ.lower() for h in high_stress_jobs):
        strategies.append(
            f"💼 Your occupation ({occ}) shows the lowest avg sleep quality in the dataset (4.0–6.0). "
            "These roles often have irregular hours and high cognitive load. "
            "Set a hard stop-work time and create a work-to-rest transition routine."
        )


    # ════════════════════════════════════════════════════════════════════════
    # 7. SCORE-BAND OVERALL MESSAGE
    # ════════════════════════════════════════════════════════════════════════
    if score < 5:
        overall = (
            "🔴 Critical sleep quality. Multiple factors are working against you. "
            "Focus on the priority fixes above first — stress and sleep duration are your biggest levers."
        )
    elif score < 6:
        overall = (
            "🟠 Poor sleep quality. You're in the bottom 8% of the dataset. "
            "Fixing 1–2 of the issues above can move you to Fair within 2 weeks."
        )
    elif score < 7:
        overall = (
            "🟡 Fair sleep quality — the most common range (42% of dataset). "
            "You're close to Good. Small consistent changes make the difference here."
        )
    elif score < 8:
        overall = (
            "🟢 Good sleep quality. You're above average. "
            "Fine-tune your activity levels and stress management to push into Excellent."
        )
    else:
        overall = (
            "🌟 Excellent sleep quality — top tier in the dataset. "
            "Keep your current routine. Focus on consistency, not change."
        )

    return {
        "overall": overall,
        "priority_fixes": priority,
        "strategies": strategies,
        "warnings": warnings,
        "positives": positives,
    }