"""Temporal key construction for H4 timestamped context rows."""

from __future__ import annotations

import pandas as pd


def event_date(event_time: str) -> str:
    if not event_time:
        return ""
    parsed = pd.to_datetime(event_time, errors="coerce")
    if pd.isna(parsed):
        text = str(event_time).strip()
        return text[:10] if len(text) >= 10 else ""
    return parsed.date().isoformat()


def temporal_key_class(event_time: str, scenario_start: str, scenario_end: str) -> str:
    if not event_time:
        return "TEMPORAL_KEY_INCOMPLETE"
    parsed = pd.to_datetime(event_time, errors="coerce")
    if pd.isna(parsed):
        return "TEMPORAL_KEY_INCOMPLETE"
    if _has_time_component(parsed):
        return "EXACT_EVENT_TIMESTAMP"
    if scenario_start and scenario_end:
        return "SCENARIO_PERIOD_TIMESTAMP"
    return "DATE_ONLY_TIMESTAMP"


def _has_time_component(parsed) -> bool:
    try:
        return parsed.hour != 0 or parsed.minute != 0 or parsed.second != 0
    except AttributeError:
        return False
