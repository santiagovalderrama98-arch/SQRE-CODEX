from __future__ import annotations

import pandas as pd

from sqre.transition_engine.transition_engine_pipeline import run_transition_engine


def test_transition_engine_pipeline_writes_outputs_without_crossing_groups(tmp_path) -> None:
    states_path = tmp_path / "market_states.csv"
    output_dir = tmp_path / "processed"
    report_path = tmp_path / "transition_engine_report.txt"
    pd.DataFrame(
        {
            "State_ID": ["S1", "S2", "S3", "S4", "S5", "S6"],
            "Structure_ID": ["ST1", "ST2", "ST3", "ST4", "ST5", "ST6"],
            "Symbol": ["EURUSD", "EURUSD", "EURUSD", "GBPUSD", "GBPUSD", "EURUSD"],
            "Timeframe": ["M5", "M5", "M5", "M5", "M5", "H1"],
            "Start_Time": [
                "2026-01-01 00:00:00",
                "2026-01-01 00:05:00",
                "2026-01-01 00:10:00",
                "2026-01-01 00:00:00",
                "2026-01-01 00:05:00",
                "2026-01-01 00:00:00",
            ],
            "End_Time": [
                "2026-01-01 00:05:00",
                "2026-01-01 00:10:00",
                "2026-01-01 00:15:00",
                "2026-01-01 00:05:00",
                "2026-01-01 00:10:00",
                "2026-01-01 01:00:00",
            ],
            "Direction": ["UP", "UP", "DOWN", "UP", "DOWN", "UP"],
            "Market_State": ["A", "B", "B", "A", "C", "D"],
            "State_Confidence": [0.5, 0.7, 0.6, 0.8, 0.5, 0.9],
            "Classification_Rule": ["rule"] * 6,
            "Persistence_Index": [0.2, 0.4, 0.3, 0.5, 0.2, 0.8],
            "Structural_Complexity": [0.4] * 6,
            "Structural_Stability": [0.7, 0.8, 0.6, 0.7, 0.5, 0.9],
            "Structural_Efficiency": [0.6, 0.7, 0.4, 0.6, 0.4, 0.8],
            "Event_Density": [0.4] * 6,
            "Structural_Volatility": [0.3, 0.2, 0.5, 0.3, 0.6, 0.2],
            "Structural_Symmetry": [0.8] * 6,
            "Structural_Confidence": [0.7, 0.8, 0.6, 0.7, 0.6, 0.9],
            "Lifecycle_Stage": ["MATURITY"] * 6,
            "Duration_Seconds": [300, 300, 300, 300, 300, 3600],
            "Price_Displacement": [0.001, 0.002, -0.001, 0.001, -0.002, 0.003],
            "Event_Count": [5, 6, 7, 4, 5, 8],
            "Leg_Count": [2, 3, 3, 2, 2, 4],
        }
    ).to_csv(states_path, index=False)

    summary = run_transition_engine(states_path, output_dir, report_path)

    assert summary.states_processed == 6
    assert summary.transitions_generated == 3
    assert (output_dir / "state_transitions.csv").exists()
    assert (output_dir / "transition_matrix.csv").exists()
    assert (output_dir / "transition_sequences.csv").exists()
    assert report_path.exists()

    transitions = pd.read_csv(output_dir / "state_transitions.csv")
    matrix = pd.read_csv(output_dir / "transition_matrix.csv")
    sequences = pd.read_csv(output_dir / "transition_sequences.csv")

    assert len(transitions) == 3
    assert {
        "Transition_ID",
        "From_State_ID",
        "To_State_ID",
        "From_Market_State",
        "To_Market_State",
        "Transition_Magnitude",
    }.issubset(transitions.columns)
    assert {
        "From_State",
        "To_State",
        "Count",
        "Probability",
        "Average_Transition_Magnitude",
    }.issubset(matrix.columns)
    assert {
        "Sequence_ID",
        "Sequence",
        "Length",
        "Count",
        "Average_Transition_Magnitude",
    }.issubset(sequences.columns)
    assert not ((transitions["Symbol"] == "EURUSD") & (transitions["To_State_ID"] == "S4")).any()
    assert not ((transitions["Timeframe"] == "M5") & (transitions["To_State_ID"] == "S6")).any()
