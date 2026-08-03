"""D1 same-time context index for H4/D1 alignment."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_alignment_table.models import D1ContextMatch


class D1ContextIndex:
    """Find contemporaneous D1 context for an H4 timestamp."""

    def __init__(self, d1_states: pd.DataFrame, candle_alignment_map: pd.DataFrame | None = None) -> None:
        self.d1_states = _normalize_d1_states(d1_states)
        self.candle_alignment_map = _normalize_candle_map(candle_alignment_map if candle_alignment_map is not None else pd.DataFrame())

    def match(self, timestamp: object, date_value: object) -> D1ContextMatch:
        resolved_timestamp = pd.to_datetime(timestamp, errors="coerce")
        resolved_date = _date_string(date_value)
        if self.d1_states.empty:
            return _no_match("D1 timestamped state/regime context is unavailable.")

        if not pd.isna(resolved_timestamp):
            interval_match = self._interval_match(resolved_timestamp)
            if interval_match is not None:
                return D1ContextMatch(
                    interval_match,
                    "D1_INTERVAL_CONTAINMENT_MATCH",
                    "HIGH_CONFIDENCE_SAME_TIME_ALIGNMENT",
                    "H4 timestamp is contained within the D1 state/regime interval.",
                )

        date_match = self._date_match(resolved_date)
        if date_match is not None:
            return D1ContextMatch(
                date_match,
                "D1_DATE_MATCH",
                "MODERATE_CONFIDENCE_SAME_TIME_ALIGNMENT",
                "H4 date matched the D1 state/regime date.",
            )

        mapped_date = self._mapped_d1_date(resolved_timestamp, resolved_date)
        mapped_match = self._date_match(mapped_date)
        if mapped_match is not None:
            return D1ContextMatch(
                mapped_match,
                "H4_D1_CANDLE_MAP_DATE_MATCH",
                "LOW_CONFIDENCE_SAME_TIME_ALIGNMENT",
                "H4 timestamp/date was mapped to D1 date through the candle alignment map.",
            )

        return _no_match("No same-time D1 state/regime context matched the H4 timestamp or date.")

    def _interval_match(self, timestamp: pd.Timestamp) -> dict[str, object] | None:
        if "D1_Period_Start" not in self.d1_states.columns or "D1_Period_End" not in self.d1_states.columns:
            return None
        candidates = self.d1_states[
            (self.d1_states["D1_Period_Start"].notna())
            & (self.d1_states["D1_Period_End"].notna())
            & (self.d1_states["D1_Period_Start"] <= timestamp)
            & (timestamp <= self.d1_states["D1_Period_End"])
        ]
        return _first_record(candidates)

    def _date_match(self, date_value: str) -> dict[str, object] | None:
        if not date_value or "D1_Date" not in self.d1_states.columns:
            return None
        candidates = self.d1_states[self.d1_states["D1_Date"].astype(str) == date_value]
        return _first_record(candidates)

    def _mapped_d1_date(self, timestamp: pd.Timestamp, date_value: str) -> str:
        if self.candle_alignment_map.empty:
            return ""
        candidates = pd.DataFrame()
        if not pd.isna(timestamp) and "H4_Timestamp" in self.candle_alignment_map.columns:
            candidates = self.candle_alignment_map[self.candle_alignment_map["H4_Timestamp"] == timestamp]
        if candidates.empty and date_value and "H4_Date" in self.candle_alignment_map.columns:
            candidates = self.candle_alignment_map[self.candle_alignment_map["H4_Date"].astype(str) == date_value]
        if candidates.empty or "D1_Date" not in candidates.columns:
            return ""
        return str(candidates.iloc[0]["D1_Date"])


def _normalize_d1_states(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    normalized = frame.copy()
    for column in ["D1_Period_Start", "D1_Period_End"]:
        if column in normalized.columns:
            normalized[column] = pd.to_datetime(normalized[column], errors="coerce")
    if "D1_Date" not in normalized.columns and "D1_Period_Start" in normalized.columns:
        normalized["D1_Date"] = normalized["D1_Period_Start"].dt.date.astype(str)
    if "D1_Date" in normalized.columns:
        normalized["D1_Date"] = normalized["D1_Date"].astype(str)
    sort_columns = [column for column in ["D1_Period_Start", "D1_Date"] if column in normalized.columns]
    if not sort_columns:
        return normalized
    return normalized.sort_values(sort_columns)


def _normalize_candle_map(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    normalized = frame.copy()
    if "H4_Timestamp" in normalized.columns:
        normalized["H4_Timestamp"] = pd.to_datetime(normalized["H4_Timestamp"], errors="coerce")
    for column in ["H4_Date", "D1_Date"]:
        if column in normalized.columns:
            normalized[column] = normalized[column].astype(str)
    return normalized


def _first_record(frame: pd.DataFrame) -> dict[str, object] | None:
    if frame.empty:
        return None
    return frame.iloc[0].to_dict()


def _date_string(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    parsed = pd.to_datetime(value, errors="coerce")
    if not pd.isna(parsed):
        return parsed.date().isoformat()
    return str(value)


def _no_match(diagnostic: str) -> D1ContextMatch:
    return D1ContextMatch(
        None,
        "NO_D1_SAME_TIME_MATCH",
        "NO_SAME_TIME_ALIGNMENT_CONFIDENCE",
        diagnostic,
    )
