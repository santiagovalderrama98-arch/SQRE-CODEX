"""CSV loaders for SQRE Price Outcome Research."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.price_outcome_research.models import OHLCCandle, PriceOutcomeState, PriceOutcomeTransition


STATE_REQUIRED_COLUMNS = [
    "State_ID",
    "Structure_ID",
    "Symbol",
    "Timeframe",
    "Start_Time",
    "End_Time",
    "Direction",
    "Market_State",
    "State_Confidence",
]

STATE_OPTIONAL_DEFAULTS: dict[str, Any] = {
    "Duration_Seconds": 0.0,
    "Price_Displacement": 0.0,
}

TRANSITION_REQUIRED_COLUMNS = [
    "Transition_ID",
    "From_State_ID",
    "To_State_ID",
    "From_Structure_ID",
    "To_Structure_ID",
    "Symbol",
    "Timeframe",
    "From_Market_State",
    "To_Market_State",
    "Transition_Label",
    "Start_Time",
    "End_Time",
    "From_Direction",
    "To_Direction",
    "Primary_Transition_Type",
    "Transition_Tags",
    "Transition_Magnitude",
    "Transition_Stability",
]

OHLC_REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


def load_price_outcome_states(path: Path | str) -> list[PriceOutcomeState]:
    frame = _read_csv(path, "market states")
    _validate_columns(frame, STATE_REQUIRED_COLUMNS, "market_states.csv")
    frame = _with_defaults(frame, STATE_OPTIONAL_DEFAULTS)
    frame["Start_Time"] = pd.to_datetime(frame["Start_Time"])
    frame["End_Time"] = pd.to_datetime(frame["End_Time"])
    frame = frame.sort_values(["Symbol", "Timeframe", "Start_Time"]).reset_index(drop=True)
    return [_state_from_row(row) for _, row in frame.iterrows()]


def load_price_outcome_transitions(path: Path | str) -> list[PriceOutcomeTransition]:
    frame = _read_csv(path, "state transitions")
    _validate_columns(frame, TRANSITION_REQUIRED_COLUMNS, "state_transitions.csv")
    frame["Start_Time"] = pd.to_datetime(frame["Start_Time"])
    frame["End_Time"] = pd.to_datetime(frame["End_Time"])
    frame = frame.sort_values(["Symbol", "Timeframe", "Start_Time"]).reset_index(drop=True)
    return [_transition_from_row(row) for _, row in frame.iterrows()]


def load_ohlc(path: Path | str) -> list[OHLCCandle]:
    frame = _read_csv(path, "OHLC")
    _validate_columns(frame, OHLC_REQUIRED_COLUMNS, "OHLC CSV")
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values("Date").reset_index(drop=True)
    return [_candle_from_row(row) for _, row in frame.iterrows()]


def _read_csv(path: Path | str, label: str) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"{label} file not found: {csv_path}")
    return pd.read_csv(csv_path)


def _validate_columns(frame: pd.DataFrame, required: list[str], source: str) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(missing)}")


def _with_defaults(frame: pd.DataFrame, defaults: dict[str, Any]) -> pd.DataFrame:
    frame = frame.copy()
    for column, default in defaults.items():
        if column not in frame.columns:
            frame[column] = default
        else:
            frame[column] = frame[column].fillna(default)
    return frame


def _state_from_row(row: pd.Series) -> PriceOutcomeState:
    return PriceOutcomeState(
        state_id=str(row["State_ID"]),
        structure_id=str(row["Structure_ID"]),
        symbol=str(row["Symbol"]),
        timeframe=str(row["Timeframe"]),
        start_time=row["Start_Time"].to_pydatetime(),
        end_time=row["End_Time"].to_pydatetime(),
        direction=str(row["Direction"]),
        market_state=str(row["Market_State"]),
        state_confidence=float(row["State_Confidence"]),
        duration_seconds=float(row["Duration_Seconds"]),
        price_displacement=float(row["Price_Displacement"]),
    )


def _transition_from_row(row: pd.Series) -> PriceOutcomeTransition:
    return PriceOutcomeTransition(
        transition_id=str(row["Transition_ID"]),
        from_state_id=str(row["From_State_ID"]),
        to_state_id=str(row["To_State_ID"]),
        from_structure_id=str(row["From_Structure_ID"]),
        to_structure_id=str(row["To_Structure_ID"]),
        symbol=str(row["Symbol"]),
        timeframe=str(row["Timeframe"]),
        from_market_state=str(row["From_Market_State"]),
        to_market_state=str(row["To_Market_State"]),
        transition_label=str(row["Transition_Label"]),
        start_time=row["Start_Time"].to_pydatetime(),
        end_time=row["End_Time"].to_pydatetime(),
        from_direction=str(row["From_Direction"]),
        to_direction=str(row["To_Direction"]),
        primary_transition_type=str(row["Primary_Transition_Type"]),
        transition_tags=str(row["Transition_Tags"]),
        transition_magnitude=float(row["Transition_Magnitude"]),
        transition_stability=float(row["Transition_Stability"]),
    )


def _candle_from_row(row: pd.Series) -> OHLCCandle:
    return OHLCCandle(
        date=row["Date"].to_pydatetime(),
        open=float(row["Open"]),
        high=float(row["High"]),
        low=float(row["Low"]),
        close=float(row["Close"]),
        volume=float(row["Volume"]),
    )
