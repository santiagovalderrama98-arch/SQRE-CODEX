"""CSV and value normalization helpers for H4 timestamped state/transition outputs."""

from __future__ import annotations

from datetime import datetime
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
STATE_START_ALIASES = ["State_Start_Time", "Start_Time", "Structure_Start", "Period_Start"]
STATE_END_ALIASES = ["State_End_Time", "End_Time", "Structure_End", "Period_End"]
SCENARIO_ALIASES = ["Scenario_ID", "Validation_Scenario_ID", "Sample_ID", "Period_ID"]
SYMBOL_ALIASES = ["Symbol", "symbol"]
TIMEFRAME_ALIASES = ["Timeframe", "TF", "timeframe"]
STATE_ALIASES = ["State", "Market_State", "State_Label", "Condition_Label", "Current_State"]
SOURCE_STATE_ALIASES = ["Source_State", "From_State", "Previous_State", "State_From", "Current_State"]
TARGET_STATE_ALIASES = ["Target_State", "To_State", "Next_State", "State_To", "New_State"]
TRANSITION_ALIASES = ["Transition_Label", "Transition", "State_Transition", "Condition_Label"]
CONFIDENCE_ALIASES = ["State_Confidence", "Confidence", "Classification_Confidence", "Structure_Quality"]
STRUCTURE_ID_ALIASES = ["Structure_ID", "Structural_Unit_ID", "Structural_ID"]
STRUCTURE_DIRECTION_ALIASES = ["Structure_Direction", "Direction", "Structural_Direction"]
STRUCTURAL_EFFICIENCY_ALIASES = ["Structural_Efficiency", "Efficiency"]
STRUCTURAL_CONFIDENCE_ALIASES = ["Structural_Confidence", "Structure_Confidence", "Confidence"]
PERIOD_START_ALIASES = ["Period_Start", "Scenario_Start", "Start_Date", "From_Date"]
PERIOD_END_ALIASES = ["Period_End", "Scenario_End", "End_Date", "To_Date"]
OHLC_FILE_ALIASES = ["OHLC_File", "Ohlc_File", "Input_File", "Raw_File", "Raw_OHLC_File"]
STATUS_ALIASES = ["Scenario_Status", "Status", "Validation_Status"]
STATES_GENERATED_ALIASES = ["States_Generated", "State_Count", "Market_State_Count"]
TRANSITIONS_GENERATED_ALIASES = ["Transitions_Generated", "Transition_Count", "State_Transition_Count"]


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


def iso_date(raw: str) -> str:
    if not raw:
        return ""
    parsed = pd.to_datetime(raw, errors="coerce")
    if pd.isna(parsed):
        return ""
    return parsed.date().isoformat()


def stable_time(raw: str) -> str:
    if not raw:
        return ""
    parsed = pd.to_datetime(raw, errors="coerce")
    if pd.isna(parsed):
        return str(raw).strip()
    value: datetime = parsed.to_pydatetime()
    return value.replace(tzinfo=None).isoformat(sep=" ")
