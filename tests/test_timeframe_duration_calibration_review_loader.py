from pathlib import Path

import pandas as pd
import pytest

from sqre.timeframe_duration_calibration_review.loader import load_duration_experiment_summary


def test_loader_reads_synthetic_experiment_summary(tmp_path: Path):
    summary = tmp_path / "summary.csv"
    pd.DataFrame([_row("one", "H1", "h1_duration_24h_baseline")]).to_csv(summary, index=False)

    rows = load_duration_experiment_summary(summary)

    assert len(rows) == 1
    assert rows[0].scenario_id == "one"
    assert rows[0].experiment_profile == "h1_duration_24h_baseline"


def test_loader_handles_case_insensitive_required_columns(tmp_path: Path):
    summary = tmp_path / "summary.csv"
    row = {key.lower(): value for key, value in _row("one", "M5", "m5_duration_4h_baseline").items()}
    pd.DataFrame([row]).to_csv(summary, index=False)

    rows = load_duration_experiment_summary(summary)

    assert rows[0].timeframe == "M5"
    assert rows[0].experiment_profile == "m5_duration_4h_baseline"


def test_loader_maps_existing_experiment_id_column_to_profile(tmp_path: Path):
    summary = tmp_path / "summary.csv"
    row = _row("one", "H1", "h1_duration_18h")
    row["Experiment_ID"] = row.pop("Experiment_Profile")
    pd.DataFrame([row]).to_csv(summary, index=False)

    rows = load_duration_experiment_summary(summary)

    assert rows[0].experiment_profile == "h1_duration_18h"


def test_loader_fills_missing_optional_count_columns_with_zero(tmp_path: Path):
    summary = tmp_path / "summary.csv"
    row = _row("one", "H1", "h1_duration_18h")
    row.pop("Directional_Displacement_Count")
    row.pop("States_Generated")
    pd.DataFrame([row]).to_csv(summary, index=False)

    rows = load_duration_experiment_summary(summary)

    assert rows[0].directional_displacement_count == 0
    assert rows[0].states_generated == 0


def test_loader_fails_clearly_when_required_columns_are_missing(tmp_path: Path):
    summary = tmp_path / "summary.csv"
    row = _row("one", "H1", "h1_duration_18h")
    row.pop("Scenario_ID")
    pd.DataFrame([row]).to_csv(summary, index=False)

    with pytest.raises(ValueError, match="Missing required duration review column"):
        load_duration_experiment_summary(summary)


def _row(scenario_id: str, timeframe: str, profile: str) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": timeframe,
        "Experiment_Profile": profile,
        "Status": "COMPLETED",
        "Max_Structure_Duration_Seconds": 86400 if timeframe == "H1" else 14400,
        "Structures_Detected": 10,
        "Average_Structure_Duration": 3600,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Average_Forward_Range_Pips": 12,
        "Direction_Alignment_Rate": 0.55,
        "Low_Sample_Conditions_Research": 10,
        "Low_Sample_Conditions_Price_Outcome": 8,
        "States_Generated": 10,
        "Directional_Displacement_Count": 3,
        "Directional_Expansion_Count": 2,
        "Directional_Drift_Count": 1,
        "Volatile_Rotation_Count": 1,
        "Complex_Consolidation_Count": 2,
        "Low_Quality_Structure_Count": 1,
        "Unclassified_Count": 0,
        "Average_Outcome_Magnitude_Pips": 6,
    }
