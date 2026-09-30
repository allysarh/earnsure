"""Lean weeks, drops and recovery (TD §7.7, §7.9)."""

from datetime import timedelta

import numpy as np

from . import config, data_gen, fmt


def reference(weekly: np.ndarray) -> np.ndarray:
    """Median of the previous 8 weeks (at least 4), i.e. shift(1).rolling(8, 4).median()."""
    ref = np.full(len(weekly), np.nan)
    for i in range(len(weekly)):
        window = weekly[max(0, i - config.LEAN_REF_WINDOW):i]
        if len(window) >= config.LEAN_REF_MIN_PERIODS:
            ref[i] = np.median(window)
    return ref


def lean_weeks(weekly: np.ndarray) -> np.ndarray:
    ref = reference(weekly)
    with np.errstate(invalid="ignore"):
        return weekly < config.LEAN_THRESHOLD * ref


def lean_periods(weekly: np.ndarray) -> list[dict]:
    lean, ref = lean_weeks(weekly), reference(weekly)
    periods, i = [], 0
    while i < len(weekly):
        if not lean[i]:
            i += 1
            continue
        start = i
        while i < len(weekly) and lean[i]:
            i += 1
        end = i - 1
        target = config.RECOVERY_THRESHOLD * ref[start]
        rec = next((j for j in range(end + 1, len(weekly)) if weekly[j] >= target), None)
        periods.append({
            "start_week": start, "end_week": end, "weeks": end - start + 1,
            "start": data_gen.week_start(start), "end": data_gen.week_start(end) + timedelta(days=6),
            "recovered_week": rec,
            "recovered": data_gen.week_start(rec) if rec is not None else None,
            "weeks_to_recover": rec - start if rec is not None else None,
        })
    return periods


def describe_period(p: dict) -> dict:
    return {
        "range": f"{p['start'].day} – {fmt.day_month(p['end'])}"
                 if p["start"].month == p["end"].month
                 else f"{fmt.day_month(p['start'])} – {fmt.day_month(p['end'])}",
        "weeks": p["weeks"],
        "weeks_to_recover": p["weeks_to_recover"],
        "recovered_by": fmt.day_month(p["recovered"]) if p["recovered"] else None,
        "period_start": p["start"].isoformat(),
        "month_label": p["start"].strftime("%B %Y"),
    }
