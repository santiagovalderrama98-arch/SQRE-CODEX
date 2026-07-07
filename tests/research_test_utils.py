from __future__ import annotations

from pathlib import Path

import pandas as pd


STATE_ROWS = {
    "State_ID": ["S1", "S2", "S3", "S4", "S5", "S6"],
    "Structure_ID": ["ST1", "ST2", "ST3", "ST4", "ST5", "ST6"],
    "Symbol": ["EURUSD"] * 6,
    "Timeframe": ["M5"] * 6,
    "Start_Time": [
        "2026-01-01 00:00:00",
        "2026-01-01 00:05:00",
        "2026-01-01 00:10:00",
        "2026-01-01 00:15:00",
        "2026-01-01 00:20:00",
        "2026-01-01 00:25:00",
    ],
    "End_Time": [
        "2026-01-01 00:05:00",
        "2026-01-01 00:10:00",
        "2026-01-01 00:15:00",
        "2026-01-01 00:20:00",
        "2026-01-01 00:25:00",
        "2026-01-01 00:30:00",
    ],
    "Direction": ["UP", "UP", "DOWN", "DOWN", "UP", "UP"],
    "Market_State": ["A", "B", "A", "C", "B", "A"],
    "State_Confidence": [0.60, 0.70, 0.65, 0.50, 0.80, 0.55],
    "Classification_Rule": ["rule"] * 6,
    "Persistence_Index": [0.2, 0.3, 0.4, 0.2, 0.5, 0.3],
    "Structural_Complexity": [0.4] * 6,
    "Structural_Stability": [0.6, 0.7, 0.6, 0.4, 0.8, 0.5],
    "Structural_Efficiency": [0.6] * 6,
    "Event_Density": [0.4] * 6,
    "Structural_Volatility": [0.3] * 6,
    "Structural_Symmetry": [0.8] * 6,
    "Structural_Confidence": [0.6, 0.7, 0.6, 0.5, 0.8, 0.5],
    "Lifecycle_Stage": ["MATURITY"] * 6,
    "Duration_Seconds": [300] * 6,
    "Price_Displacement": [0.0] * 6,
    "Event_Count": [5] * 6,
    "Leg_Count": [2] * 6,
}


TRANSITION_ROWS = {
    "Transition_ID": ["T1", "T2", "T3", "T4", "T5"],
    "From_State_ID": ["S1", "S2", "S3", "S4", "S5"],
    "To_State_ID": ["S2", "S3", "S4", "S5", "S6"],
    "From_Structure_ID": ["ST1", "ST2", "ST3", "ST4", "ST5"],
    "To_Structure_ID": ["ST2", "ST3", "ST4", "ST5", "ST6"],
    "Symbol": ["EURUSD"] * 5,
    "Timeframe": ["M5"] * 5,
    "From_Market_State": ["A", "B", "A", "C", "B"],
    "To_Market_State": ["B", "A", "C", "B", "A"],
    "Transition_Label": ["A -> B", "B -> A", "A -> C", "C -> B", "B -> A"],
    "Start_Time": [
        "2026-01-01 00:05:00",
        "2026-01-01 00:10:00",
        "2026-01-01 00:15:00",
        "2026-01-01 00:20:00",
        "2026-01-01 00:25:00",
    ],
    "End_Time": [
        "2026-01-01 00:10:00",
        "2026-01-01 00:15:00",
        "2026-01-01 00:20:00",
        "2026-01-01 00:25:00",
        "2026-01-01 00:30:00",
    ],
    "Transition_Duration_Seconds": [300] * 5,
    "From_Direction": ["UP", "UP", "DOWN", "DOWN", "UP"],
    "To_Direction": ["UP", "DOWN", "DOWN", "UP", "UP"],
    "State_Changed": [True] * 5,
    "Direction_Changed": [False, True, False, True, False],
    "Primary_Transition_Type": ["STATE_CHANGE"] * 5,
    "Transition_Tags": [
        "CONFIDENCE_EXPANSION|LOW_MAGNITUDE",
        "CONFIDENCE_STABLE|LOW_MAGNITUDE",
        "CONFIDENCE_DETERIORATION|MODERATE_MAGNITUDE",
        "CONFIDENCE_EXPANSION|LOW_MAGNITUDE",
        "CONFIDENCE_DETERIORATION|LOW_MAGNITUDE",
    ],
    "Transition_Magnitude": [0.10, 0.20, 0.30, 0.15, 0.25],
    "Transition_Stability": [0.80, 0.70, 0.60, 0.75, 0.65],
    "State_Confidence_Change": [0.10, -0.05, -0.15, 0.30, -0.25],
    "Structural_Quality_Change": [0.10, 0.00, -0.10, 0.20, -0.15],
}


def write_sample_inputs(tmp_path: Path) -> tuple[Path, Path]:
    states_path = tmp_path / "market_states.csv"
    transitions_path = tmp_path / "state_transitions.csv"
    pd.DataFrame(STATE_ROWS).to_csv(states_path, index=False)
    pd.DataFrame(TRANSITION_ROWS).to_csv(transitions_path, index=False)
    return states_path, transitions_path
