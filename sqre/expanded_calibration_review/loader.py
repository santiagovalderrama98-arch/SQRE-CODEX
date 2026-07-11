"""Load expanded historical validation summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.expanded_calibration_review.models import ExpandedValidationScenarioSummary


def load_expanded_summary_csv(path: Path | str) -> list[ExpandedValidationScenarioSummary]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Expanded historical summary CSV not found: {csv_path}")
    frame = pd.read_csv(csv_path)
    return [_row_to_summary(row, csv_path) for _, row in frame.iterrows()]


def load_expanded_summaries(paths: list[Path | str]) -> list[ExpandedValidationScenarioSummary]:
    rows: list[ExpandedValidationScenarioSummary] = []
    for path in paths:
        rows.extend(load_expanded_summary_csv(path))
    return rows


def _row_to_summary(row: pd.Series, source_file: Path) -> ExpandedValidationScenarioSummary:
    return ExpandedValidationScenarioSummary(
        scenario_id=_text(row, "Scenario_ID"),
        timeframe=_text(row, "Timeframe"),
        ohlc_rows=_integer(row, "OHLC_Rows"),
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
        low_quality_structure_count=_integer(row, "Low_Quality_Structure_Count"),
        unclassified_count=_integer(row, "Unclassified_Count"),
        average_forward_range_pips=_number(row, "Average_Forward_Range_Pips"),
        average_outcome_magnitude_pips=_number(row, "Average_Outcome_Magnitude_Pips"),
        direction_alignment_rate=_number(row, "Direction_Alignment_Rate"),
        low_sample_conditions_research=_integer(row, "Low_Sample_Conditions_Research"),
        low_sample_conditions_price_outcome=_integer(row, "Low_Sample_Conditions_Price_Outcome"),
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
