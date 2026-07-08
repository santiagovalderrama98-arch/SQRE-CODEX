"""Load validation summary CSV files for calibration review."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.calibration_review.models import ValidationScenarioSummary


def load_validation_summary_csv(path: Path | str) -> list[ValidationScenarioSummary]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Validation summary CSV not found: {csv_path}")
    frame = pd.read_csv(csv_path)
    return [_row_to_summary(row, csv_path) for _, row in frame.iterrows()]


def load_validation_summaries(paths: list[Path | str]) -> list[ValidationScenarioSummary]:
    deduped: dict[tuple[str, str, str], ValidationScenarioSummary] = {}
    for path in paths:
        for row in load_validation_summary_csv(path):
            key = (row.scenario_id, row.period_start, row.period_end)
            deduped[key] = row
    return list(deduped.values())


def _row_to_summary(row: pd.Series, source_file: Path) -> ValidationScenarioSummary:
    return ValidationScenarioSummary(
        scenario_id=_text(row, "Scenario_ID"),
        status=_text(row, "Status"),
        symbol=_text(row, "Symbol"),
        timeframe=_text(row, "Timeframe"),
        period_start=_text(row, "Period_Start"),
        period_end=_text(row, "Period_End"),
        ohlc_rows=_integer(row, "OHLC_Rows"),
        max_structure_duration_seconds=_integer(row, "Max_Structure_Duration_Seconds"),
        forward_windows=_text(row, "Forward_Windows"),
        structures_detected=_integer(row, "Structures_Detected"),
        average_structure_duration=_number(row, "Average_Structure_Duration"),
        states_generated=_integer(row, "States_Generated"),
        unique_states=_integer(row, "Unique_States"),
        most_common_state=_text(row, "Most_Common_State"),
        directional_displacement_count=_integer(row, "Directional_Displacement_Count"),
        directional_expansion_count=_integer(row, "Directional_Expansion_Count"),
        directional_drift_count=_integer(row, "Directional_Drift_Count"),
        volatile_rotation_count=_integer(row, "Volatile_Rotation_Count"),
        complex_consolidation_count=_integer(row, "Complex_Consolidation_Count"),
        neutral_compression_count=_integer(row, "Neutral_Compression_Count"),
        low_quality_structure_count=_integer(row, "Low_Quality_Structure_Count"),
        unclassified_count=_integer(row, "Unclassified_Count"),
        average_state_confidence=_number(row, "Average_State_Confidence"),
        transitions_generated=_integer(row, "Transitions_Generated"),
        unique_transitions=_integer(row, "Unique_Transitions"),
        state_change_rate=_number(row, "State_Change_Rate"),
        direction_change_rate=_number(row, "Direction_Change_Rate"),
        average_transition_magnitude=_number(row, "Average_Transition_Magnitude"),
        average_transition_stability=_number(row, "Average_Transition_Stability"),
        conditions_evaluated=_integer(row, "Conditions_Evaluated"),
        low_sample_conditions_research=_integer(row, "Low_Sample_Conditions_Research"),
        price_outcomes_generated=_integer(row, "Price_Outcomes_Generated"),
        price_outcome_summary_rows=_integer(row, "Price_Outcome_Summary_Rows"),
        low_sample_conditions_price_outcome=_integer(row, "Low_Sample_Conditions_Price_Outcome"),
        average_forward_close_return_pips=_number(row, "Average_Forward_Close_Return_Pips"),
        median_forward_close_return_pips=_number(row, "Median_Forward_Close_Return_Pips"),
        average_forward_range_pips=_number(row, "Average_Forward_Range_Pips"),
        average_favorable_displacement_pips=_number(row, "Average_Favorable_Displacement_Pips"),
        average_adverse_displacement_pips=_number(row, "Average_Adverse_Displacement_Pips"),
        average_outcome_magnitude_pips=_number(row, "Average_Outcome_Magnitude_Pips"),
        direction_alignment_rate=_number(row, "Direction_Alignment_Rate"),
        source_file=str(source_file),
    )


def _text(row: pd.Series, column: str) -> str:
    value = _value(row, column, "")
    if pd.isna(value):
        return ""
    return str(value)


def _integer(row: pd.Series, column: str) -> int:
    return int(_number(row, column))


def _number(row: pd.Series, column: str) -> float:
    value = _value(row, column, 0)
    if pd.isna(value):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _value(row: pd.Series, column: str, default: Any) -> Any:
    lookup = {_normalize(key): key for key in row.index}
    actual = lookup.get(_normalize(column))
    if actual is None:
        return default
    return row[actual]


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
