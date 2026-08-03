"""CSV loading helpers for H4 timestamped context table generation."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas.errors import EmptyDataError


TIMESTAMP_ALIASES = [
    "Timestamp",
    "Date",
    "Datetime",
    "Time",
    "Event_Time",
    "State_Time",
    "Transition_Time",
    "Structure_Time",
    "Candle_Time",
]
SCENARIO_ALIASES = ["Scenario_ID", "Validation_Scenario_ID", "Sample_ID", "Period_ID"]
SOURCE_STATE_ALIASES = ["Source_State", "From_State", "Previous_State", "State_From", "Current_State"]
TARGET_STATE_ALIASES = ["Target_State", "To_State", "Next_State", "State_To", "New_State"]
SINGLE_STATE_ALIASES = ["State", "Market_State", "State_Label", "Condition_Label"]
TRANSITION_ALIASES = ["Transition_Label", "Transition", "Condition_Label", "Condition_Value", "State_Transition"]
PERIOD_START_ALIASES = ["Period_Start", "Scenario_Start", "Start_Date", "From_Date"]
PERIOD_END_ALIASES = ["Period_End", "Scenario_End", "End_Date", "To_Date"]
FORWARD_WINDOW_ALIASES = ["Forward_Window", "Forward_Window_Candles", "FW"]


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(resolved)
    except EmptyDataError:
        return pd.DataFrame()


def resolve_column(frame: pd.DataFrame, aliases: Iterable[str]) -> str | None:
    lookup = {str(column).strip().lower(): str(column) for column in frame.columns}
    for alias in aliases:
        column = lookup.get(str(alias).strip().lower())
        if column is not None:
            return column
    return None


def resolve_columns(frame: pd.DataFrame, aliases: Iterable[str]) -> list[str]:
    lookup = {str(column).strip().lower(): str(column) for column in frame.columns}
    matches: list[str] = []
    for alias in aliases:
        column = lookup.get(str(alias).strip().lower())
        if column is not None and column not in matches:
            matches.append(column)
    return matches


def row_text(row: pd.Series, aliases: Iterable[str], default: str = "") -> str:
    lookup = {str(column).strip().lower(): column for column in row.index}
    for alias in aliases:
        column = lookup.get(str(alias).strip().lower())
        if column is None:
            continue
        raw = row.get(column)
        if pd.isna(raw):
            return default
        return str(raw).strip()
    return default


def row_int(row: pd.Series, aliases: Iterable[str], default: int = 0) -> int:
    raw = row_text(row, aliases, "")
    if raw == "":
        return default
    try:
        return int(round(float(raw)))
    except ValueError:
        return default


def joined(columns: Iterable[str]) -> str:
    return "|".join(str(column) for column in columns if str(column).strip())


def normalized_key(value: object) -> str:
    text = "" if pd.isna(value) else str(value).strip()
    return text.upper()
