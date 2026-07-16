"""Load H4 state deep dive outputs for scenario dispersion review."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.h4_scenario_dispersion_review.models import (
    OutcomeStatisticsInput,
    ProfileInventoryRow,
    ScenarioComparisonInput,
)


PROFILE_INVENTORY_FILE = "h4_state_deep_dive_profile_inventory.csv"
SCENARIO_BREAKDOWN_FILE = "h4_state_scenario_breakdown.csv"
OUTCOME_STATISTICS_FILE = "h4_state_outcome_statistics.csv"
SCENARIO_COMPARISON_FILE = "h4_state_scenario_comparison_matrix.csv"
DEEP_DIVE_SUMMARY_FILE = "h4_state_deep_dive_summary.csv"


def load_profile_inventory(input_dir: Path | str) -> list[ProfileInventoryRow]:
    path = Path(input_dir) / PROFILE_INVENTORY_FILE
    if not path.exists():
        return []
    frame = pd.read_csv(path)
    return [_profile_row(row) for _, row in frame.iterrows()]


def load_outcome_statistics(input_dir: Path | str) -> list[OutcomeStatisticsInput]:
    path = Path(input_dir) / OUTCOME_STATISTICS_FILE
    if not path.exists():
        raise FileNotFoundError(f"H4 outcome statistics file not found: {path}")
    frame = pd.read_csv(path)
    return [_statistics_row(row) for _, row in frame.iterrows()]


def load_scenario_comparisons(input_dir: Path | str) -> list[ScenarioComparisonInput]:
    path = Path(input_dir) / SCENARIO_COMPARISON_FILE
    if not path.exists():
        raise FileNotFoundError(f"H4 scenario comparison matrix file not found: {path}")
    frame = pd.read_csv(path)
    return [_comparison_row(row) for _, row in frame.iterrows()]


def optional_file_status(input_dir: Path | str) -> dict[str, bool]:
    root = Path(input_dir)
    return {
        PROFILE_INVENTORY_FILE: (root / PROFILE_INVENTORY_FILE).exists(),
        SCENARIO_BREAKDOWN_FILE: (root / SCENARIO_BREAKDOWN_FILE).exists(),
        DEEP_DIVE_SUMMARY_FILE: (root / DEEP_DIVE_SUMMARY_FILE).exists(),
    }


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


def _profile_row(row: pd.Series) -> ProfileInventoryRow:
    return ProfileInventoryRow(
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        profile_type=text_value(row, "Profile_Type"),
        scenario_count=integer_value(row, "Scenario_Count"),
        scenarios_present=text_value(row, "Scenarios_Present"),
        total_sample_size=integer_value(row, "Total_Sample_Size"),
        average_sample_size_per_scenario=number_value(row, "Average_Sample_Size_Per_Scenario"),
        average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
        average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
        average_direction_alignment_rate=number_value(row, "Average_Direction_Alignment_Rate"),
        forward_range_cv=number_value(row, "Forward_Range_CV"),
        outcome_magnitude_cv=number_value(row, "Outcome_Magnitude_CV"),
        scenario_sensitivity_flag=text_value(row, "Scenario_Sensitivity_Flag"),
        sample_adequacy_flag=text_value(row, "Sample_Adequacy_Flag"),
        dispersion_class=text_value(row, "Dispersion_Class"),
        condition_research_class=text_value(row, "Condition_Research_Class"),
        profile_diagnostic=text_value(row, "Profile_Diagnostic"),
        recommended_follow_up=text_value(row, "Recommended_Follow_Up"),
    )


def _statistics_row(row: pd.Series) -> OutcomeStatisticsInput:
    return OutcomeStatisticsInput(
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        profile_type=text_value(row, "Profile_Type"),
        scenario_count=integer_value(row, "Scenario_Count"),
        total_sample_size=integer_value(row, "Total_Sample_Size"),
        average_sample_size_per_scenario=number_value(row, "Average_Sample_Size_Per_Scenario"),
        average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
        average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
        average_direction_alignment_rate=number_value(row, "Average_Direction_Alignment_Rate"),
        forward_range_cv=number_value(row, "Forward_Range_CV"),
        outcome_magnitude_cv=number_value(row, "Outcome_Magnitude_CV"),
        direction_alignment_dispersion=number_value(row, "Direction_Alignment_Dispersion"),
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
    )


def _resolve_index(row: pd.Series, target: str) -> str | None:
    lookup = {_normalize(column): str(column) for column in row.index}
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
