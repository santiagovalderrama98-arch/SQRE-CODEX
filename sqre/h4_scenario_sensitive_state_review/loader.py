"""Load Phase 7.5.5 and H4 state deep dive outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.h4_scenario_sensitive_state_review.models import (
    ScenarioBreakdownInput,
    ScenarioComparisonInput,
    ScenarioSensitiveProfileInput,
)


SCENARIO_SENSITIVE_PROFILES_FILE = "h4_scenario_sensitive_profiles.csv"
SCENARIO_COMPARISON_FILE = "h4_state_scenario_comparison_matrix.csv"
SCENARIO_BREAKDOWN_FILE = "h4_state_scenario_breakdown.csv"

OPTIONAL_DISPERSION_FILES = [
    "h4_profile_dispersion_diagnostics.csv",
    "h4_scenario_dispersion_contribution.csv",
    "h4_state_dispersion_summary.csv",
    "h4_forward_window_dispersion_summary.csv",
    "h4_sample_constrained_profiles.csv",
    "h4_scenario_dispersion_review_summary.csv",
]
OPTIONAL_DEEP_DIVE_FILES = [
    "h4_state_outcome_statistics.csv",
    "h4_state_deep_dive_profile_inventory.csv",
]


def load_scenario_sensitive_profiles(dispersion_review_dir: Path | str) -> list[ScenarioSensitiveProfileInput]:
    path = Path(dispersion_review_dir) / SCENARIO_SENSITIVE_PROFILES_FILE
    if not path.exists():
        raise FileNotFoundError(f"H4 scenario-sensitive profiles file not found: {path}")
    frame = pd.read_csv(path)
    return [_profile_row(row) for _, row in frame.iterrows()]


def load_scenario_comparisons(state_deep_dive_dir: Path | str) -> list[ScenarioComparisonInput]:
    path = Path(state_deep_dive_dir) / SCENARIO_COMPARISON_FILE
    if not path.exists():
        raise FileNotFoundError(f"H4 scenario comparison matrix file not found: {path}")
    frame = pd.read_csv(path)
    return [_comparison_row(row) for _, row in frame.iterrows()]


def load_scenario_breakdown(state_deep_dive_dir: Path | str) -> list[ScenarioBreakdownInput]:
    path = Path(state_deep_dive_dir) / SCENARIO_BREAKDOWN_FILE
    if not path.exists():
        raise FileNotFoundError(f"H4 state scenario breakdown file not found: {path}")
    frame = pd.read_csv(path)
    return [_breakdown_row(row) for _, row in frame.iterrows()]


def optional_file_status(dispersion_review_dir: Path | str, state_deep_dive_dir: Path | str) -> dict[str, bool]:
    dispersion_root = Path(dispersion_review_dir)
    deep_dive_root = Path(state_deep_dive_dir)
    status = {name: (dispersion_root / name).exists() for name in OPTIONAL_DISPERSION_FILES}
    status.update({name: (deep_dive_root / name).exists() for name in OPTIONAL_DEEP_DIVE_FILES})
    return status


def value(row: pd.Series, column: str, default: Any = "") -> Any:
    actual = _resolve_index(row, column)
    if actual is None:
        return default
    item = row[actual]
    if pd.isna(item):
        return default
    return item


def text_value(row: pd.Series, column: str, default: str = "") -> str:
    item = value(row, column, default)
    return default if item is None else str(item)


def number_value(row: pd.Series, column: str, default: float = 0.0) -> float:
    item = value(row, column, default)
    try:
        return float(item)
    except (TypeError, ValueError):
        return default


def integer_value(row: pd.Series, column: str, default: int = 0) -> int:
    return int(number_value(row, column, float(default)))


def _profile_row(row: pd.Series) -> ScenarioSensitiveProfileInput:
    return ScenarioSensitiveProfileInput(
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        profile_type=text_value(row, "Profile_Type"),
        scenario_count=integer_value(row, "Scenario_Count"),
        total_sample_size=integer_value(row, "Total_Sample_Size"),
        average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
        average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
        average_direction_alignment_rate=number_value(row, "Average_Direction_Alignment_Rate"),
        forward_range_cv=number_value(row, "Forward_Range_CV"),
        outcome_magnitude_cv=number_value(row, "Outcome_Magnitude_CV"),
        direction_alignment_dispersion=number_value(row, "Direction_Alignment_Dispersion"),
        high_deviation_scenario_count=integer_value(row, "High_Deviation_Scenario_Count"),
        moderate_deviation_scenario_count=integer_value(row, "Moderate_Deviation_Scenario_Count"),
        low_deviation_scenario_count=integer_value(row, "Low_Deviation_Scenario_Count"),
        dominant_deviation_class=text_value(row, "Dominant_Deviation_Class", "LOW_DEVIATION"),
        dispersion_driver_class=text_value(row, "Dispersion_Driver_Class", "LOW_DISPERSION"),
        profile_dispersion_class=text_value(row, "Profile_Dispersion_Class", "STABLE_DESCRIPTIVE"),
        profile_research_readiness_class=text_value(row, "Profile_Research_Readiness_Class"),
        profile_dispersion_diagnostic=text_value(row, "Profile_Dispersion_Diagnostic"),
        recommended_follow_up=text_value(row, "Recommended_Follow_Up"),
    )


def _comparison_row(row: pd.Series) -> ScenarioComparisonInput:
    return ScenarioComparisonInput(
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        scenario_id=text_value(row, "Scenario_ID"),
        sample_size=integer_value(row, "Sample_Size"),
        forward_range_vs_profile_avg=number_value(row, "Forward_Range_vs_Profile_Avg"),
        outcome_magnitude_vs_profile_avg=number_value(row, "Outcome_Magnitude_vs_Profile_Avg"),
        direction_alignment_vs_profile_avg=number_value(row, "Direction_Alignment_vs_Profile_Avg"),
        scenario_deviation_class=text_value(row, "Scenario_Deviation_Class", "LOW_DEVIATION"),
        scenario_comparison_diagnostic=text_value(row, "Scenario_Comparison_Diagnostic"),
    )


def _breakdown_row(row: pd.Series) -> ScenarioBreakdownInput:
    return ScenarioBreakdownInput(
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        profile_type=text_value(row, "Profile_Type"),
        scenario_id=text_value(row, "Scenario_ID"),
        timeframe=text_value(row, "Timeframe", "H4"),
        sample_size=integer_value(row, "Sample_Size"),
        average_forward_close_return_pips=number_value(row, "Average_Forward_Close_Return_Pips"),
        median_forward_close_return_pips=number_value(row, "Median_Forward_Close_Return_Pips"),
        average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
        average_favorable_displacement_pips=number_value(row, "Average_Favorable_Displacement_Pips"),
        average_adverse_displacement_pips=number_value(row, "Average_Adverse_Displacement_Pips"),
        average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
        direction_alignment_rate=number_value(row, "Direction_Alignment_Rate"),
        sample_adequacy_flag=text_value(row, "Sample_Adequacy_Flag"),
        scenario_observation_diagnostic=text_value(row, "Scenario_Observation_Diagnostic"),
    )


def _resolve_index(row: pd.Series, target: str) -> str | None:
    lookup = {_normalize(column): str(column) for column in row.index}
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
