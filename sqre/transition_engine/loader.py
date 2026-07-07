"""Market States CSV loader for the Transition Engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.transition_engine.models import MarketStateInput


REQUIRED_COLUMNS = [
    "State_ID",
    "Structure_ID",
    "Symbol",
    "Timeframe",
    "Start_Time",
    "End_Time",
    "Direction",
    "Market_State",
    "State_Confidence",
    "Classification_Rule",
    "Persistence_Index",
    "Structural_Complexity",
    "Structural_Stability",
    "Structural_Efficiency",
    "Event_Density",
    "Structural_Volatility",
    "Structural_Symmetry",
    "Structural_Confidence",
]

OPTIONAL_DEFAULTS: dict[str, Any] = {
    "Lifecycle_Stage": "",
    "Duration_Seconds": 0.0,
    "Price_Displacement": 0.0,
    "Event_Count": 0,
    "Leg_Count": 0,
}


def load_market_states(path: Path | str) -> list[MarketStateInput]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Market states file not found: {csv_path}")

    frame = pd.read_csv(csv_path)
    _validate_required_columns(frame)
    frame = _with_optional_defaults(frame)
    frame["Start_Time"] = pd.to_datetime(frame["Start_Time"])
    frame["End_Time"] = pd.to_datetime(frame["End_Time"])
    frame = frame.sort_values(["Symbol", "Timeframe", "Start_Time"]).reset_index(drop=True)
    return [_row_to_market_state(row) for _, row in frame.iterrows()]


def _validate_required_columns(frame: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"market_states.csv is missing required columns: {', '.join(missing)}")


def _with_optional_defaults(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for column, default in OPTIONAL_DEFAULTS.items():
        if column not in frame.columns:
            frame[column] = default
        else:
            frame[column] = frame[column].fillna(default)
    return frame


def _row_to_market_state(row: pd.Series) -> MarketStateInput:
    return MarketStateInput(
        state_id=str(row["State_ID"]),
        structure_id=str(row["Structure_ID"]),
        symbol=str(row["Symbol"]),
        timeframe=str(row["Timeframe"]),
        start_time=row["Start_Time"].to_pydatetime(),
        end_time=row["End_Time"].to_pydatetime(),
        direction=str(row["Direction"]),
        market_state=str(row["Market_State"]),
        state_confidence=float(row["State_Confidence"]),
        classification_rule=str(row["Classification_Rule"]),
        persistence_index=float(row["Persistence_Index"]),
        structural_complexity=float(row["Structural_Complexity"]),
        structural_stability=float(row["Structural_Stability"]),
        structural_efficiency=float(row["Structural_Efficiency"]),
        event_density=float(row["Event_Density"]),
        structural_volatility=float(row["Structural_Volatility"]),
        structural_symmetry=float(row["Structural_Symmetry"]),
        structural_confidence=float(row["Structural_Confidence"]),
        lifecycle_stage=str(row["Lifecycle_Stage"]),
        duration_seconds=float(row["Duration_Seconds"]),
        price_displacement=float(row["Price_Displacement"]),
        event_count=int(row["Event_Count"]),
        leg_count=int(row["Leg_Count"]),
    )
