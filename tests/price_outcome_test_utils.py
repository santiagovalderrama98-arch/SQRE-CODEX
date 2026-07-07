from __future__ import annotations

from pathlib import Path

import pandas as pd


STATE_ROWS = {
    "State_ID": ["S2", "S1", "S3", "S4"],
    "Structure_ID": ["ST2", "ST1", "ST3", "ST4"],
    "Symbol": ["EURUSD"] * 4,
    "Timeframe": ["H1"] * 4,
    "Start_Time": [
        "2026-01-01 01:00:00",
        "2026-01-01 00:00:00",
        "2026-01-01 02:00:00",
        "2026-01-01 03:00:00",
    ],
    "End_Time": [
        "2026-01-01 02:00:00",
        "2026-01-01 01:00:00",
        "2026-01-01 03:00:00",
        "2026-01-01 04:00:00",
    ],
    "Direction": ["DOWN", "UP", "NEUTRAL", "UP"],
    "Market_State": ["B", "A", "A", "C"],
    "State_Confidence": [0.7, 0.6, 0.8, 0.5],
    "Duration_Seconds": [3600, 3600, 3600, 3600],
    "Price_Displacement": [-0.001, 0.001, 0.0, 0.002],
    "Extra_Column": ["x", "x", "x", "x"],
}


TRANSITION_ROWS = {
    "Transition_ID": ["T2", "T1", "T3"],
    "From_State_ID": ["S2", "S1", "S3"],
    "To_State_ID": ["S3", "S2", "S4"],
    "From_Structure_ID": ["ST2", "ST1", "ST3"],
    "To_Structure_ID": ["ST3", "ST2", "ST4"],
    "Symbol": ["EURUSD"] * 3,
    "Timeframe": ["H1"] * 3,
    "From_Market_State": ["B", "A", "A"],
    "To_Market_State": ["A", "B", "C"],
    "Transition_Label": ["B -> A", "A -> B", "A -> C"],
    "Start_Time": [
        "2026-01-01 02:00:00",
        "2026-01-01 01:00:00",
        "2026-01-01 03:00:00",
    ],
    "End_Time": [
        "2026-01-01 03:00:00",
        "2026-01-01 02:00:00",
        "2026-01-01 04:00:00",
    ],
    "From_Direction": ["DOWN", "UP", "NEUTRAL"],
    "To_Direction": ["NEUTRAL", "DOWN", "UP"],
    "Primary_Transition_Type": ["STATE_CHANGE"] * 3,
    "Transition_Tags": ["LOW_MAGNITUDE"] * 3,
    "Transition_Magnitude": [0.2, 0.1, 0.3],
    "Transition_Stability": [0.6, 0.7, 0.5],
    "Extra_Column": ["y", "y", "y"],
}


OHLC_ROWS = {
    "Date": [
        "2026-01-01 00:00:00",
        "2026-01-01 01:00:00",
        "2026-01-01 02:00:00",
        "2026-01-01 03:00:00",
        "2026-01-01 04:00:00",
        "2026-01-01 05:00:00",
        "2026-01-01 06:00:00",
    ],
    "Open": [1.1000, 1.1010, 1.1020, 1.1010, 1.1000, 1.1030, 1.1040],
    "High": [1.1010, 1.1030, 1.1025, 1.1015, 1.1035, 1.1050, 1.1045],
    "Low": [1.0990, 1.1005, 1.1000, 1.0995, 1.0990, 1.1020, 1.1030],
    "Close": [1.1005, 1.1020, 1.1010, 1.1000, 1.1030, 1.1040, 1.1035],
    "Volume": [0, 0, 0, 0, 0, 0, 0],
    "Extra_Column": ["z", "z", "z", "z", "z", "z", "z"],
}


def write_price_outcome_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    states_path = tmp_path / "market_states.csv"
    transitions_path = tmp_path / "state_transitions.csv"
    ohlc_path = tmp_path / "ohlc.csv"
    pd.DataFrame(STATE_ROWS).to_csv(states_path, index=False)
    pd.DataFrame(TRANSITION_ROWS).to_csv(transitions_path, index=False)
    pd.DataFrame(OHLC_ROWS).to_csv(ohlc_path, index=False)
    return states_path, transitions_path, ohlc_path
