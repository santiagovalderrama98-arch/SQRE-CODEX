"""Load M15 introduction review inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.m15_introduction_review.models import (
    M15Context,
    M15ValidationSummaryRow,
    OPTIONAL_COUNT_COLUMNS,
    OPTIONAL_RATIO_COLUMNS,
    REQUIRED_COLUMNS,
)


COMPLETED_STATUSES = {"COMPLETED", "SKIPPED"}

_RATIO_ALIASES = {
    "Directional_State_Ratio": ["Directional_Ratio"],
    "Complex_Consolidation_Ratio": ["Compression_Consolidation_Ratio"],
    "Volatile_Rotation_Ratio": [],
    "Low_Quality_Rate": [],
    "Unclassified_Rate": [],
}


def load_m15_validation_summary(path: Path | str) -> list[M15ValidationSummaryRow]:
    summary_path = Path(path)
    if not summary_path.exists():
        raise FileNotFoundError(f"M15 validation summary CSV not found: {summary_path}")
    frame = pd.read_csv(summary_path)
    frame = _canonicalize_columns(frame, summary_path)
    return [_row_to_model(row) for _, row in frame.iterrows()]


def load_context_from_master_summary(path: Path | str | None) -> M15Context:
    if path is None:
        return M15Context(interpretation="No M5/H1 context summary was provided.")
    summary_path = Path(path)
    if not summary_path.exists():
        return M15Context(interpretation=f"M5/H1 context summary was not found: {summary_path}")

    rows = load_m15_validation_summary(summary_path)
    m5_rows = _context_rows(rows, "M5")
    h1_rows = _context_rows(rows, "H1")
    return M15Context(
        m5_average_structures=_mean([row.structures_detected for row in m5_rows]) if m5_rows else None,
        h1_average_structures=_mean([row.structures_detected for row in h1_rows]) if h1_rows else None,
        m5_average_unique_states=_mean([row.unique_states for row in m5_rows]) if m5_rows else None,
        h1_average_unique_states=_mean([row.unique_states for row in h1_rows]) if h1_rows else None,
        m5_low_sample=_mean([row.low_sample_conditions_research for row in m5_rows]) if m5_rows else None,
        h1_low_sample=_mean([row.low_sample_conditions_research for row in h1_rows]) if h1_rows else None,
        interpretation=_context_interpretation(m5_rows, h1_rows),
    )


def _canonicalize_columns(frame: pd.DataFrame, source_path: Path) -> pd.DataFrame:
    columns = [str(column) for column in frame.columns]
    rename_map: dict[str, str] = {}
    missing: list[str] = []

    for required in REQUIRED_COLUMNS:
        actual = resolve_column(columns, required)
        if actual is None:
            missing.append(required)
        elif actual != required:
            rename_map[actual] = required

    if missing:
        raise ValueError(f"Missing required M15 review column(s) in {source_path}: {', '.join(missing)}")

    output = frame.rename(columns=rename_map).copy()
    current_columns = [str(column) for column in output.columns]
    output["__Has_Directional_Count_Columns"] = all(
        resolve_column(current_columns, column) is not None
        for column in [
            "Directional_Displacement_Count",
            "Directional_Expansion_Count",
            "Directional_Drift_Count",
        ]
    )
    output["__Has_Complex_Consolidation_Count_Column"] = (
        resolve_column(current_columns, "Complex_Consolidation_Count") is not None
    )
    output["__Has_Volatile_Rotation_Count_Column"] = resolve_column(current_columns, "Volatile_Rotation_Count") is not None
    output["__Has_Low_Quality_Count_Column"] = resolve_column(current_columns, "Low_Quality_Structure_Count") is not None
    output["__Has_Unclassified_Count_Column"] = resolve_column(current_columns, "Unclassified_Count") is not None

    for optional in OPTIONAL_COUNT_COLUMNS:
        actual = resolve_column([str(column) for column in output.columns], optional)
        if actual is None:
            output[optional] = 0
        elif actual != optional:
            output = output.rename(columns={actual: optional})
    for optional in OPTIONAL_RATIO_COLUMNS:
        actual = _resolve_any([str(column) for column in output.columns], optional, _RATIO_ALIASES.get(optional, []))
        if actual is not None and actual != optional:
            output = output.rename(columns={actual: optional})
    return output


def resolve_column(columns: list[str], target: str) -> str | None:
    lookup = {_normalize(column): column for column in columns}
    return lookup.get(_normalize(target))


def _resolve_any(columns: list[str], target: str, aliases: list[str]) -> str | None:
    for candidate in [target, *aliases]:
        actual = resolve_column(columns, candidate)
        if actual is not None:
            return actual
    return None


def _row_to_model(row: pd.Series) -> M15ValidationSummaryRow:
    return M15ValidationSummaryRow(
        scenario_id=_text(row, "Scenario_ID"),
        timeframe=_text(row, "Timeframe"),
        status=_text(row, "Status"),
        ohlc_rows=_integer(row, "OHLC_Rows"),
        structures_detected=_integer(row, "Structures_Detected"),
        average_structure_duration=_number(row, "Average_Structure_Duration"),
        unique_states=_integer(row, "Unique_States"),
        most_common_state=_text(row, "Most_Common_State"),
        average_forward_range_pips=_number(row, "Average_Forward_Range_Pips"),
        direction_alignment_rate=_number(row, "Direction_Alignment_Rate"),
        low_sample_conditions_research=_integer(row, "Low_Sample_Conditions_Research"),
        low_sample_conditions_price_outcome=_integer(row, "Low_Sample_Conditions_Price_Outcome"),
        states_generated=_integer(row, "States_Generated"),
        directional_displacement_count=_integer(row, "Directional_Displacement_Count"),
        directional_expansion_count=_integer(row, "Directional_Expansion_Count"),
        directional_drift_count=_integer(row, "Directional_Drift_Count"),
        volatile_rotation_count=_integer(row, "Volatile_Rotation_Count"),
        complex_consolidation_count=_integer(row, "Complex_Consolidation_Count"),
        low_quality_structure_count=_integer(row, "Low_Quality_Structure_Count"),
        unclassified_count=_integer(row, "Unclassified_Count"),
        average_outcome_magnitude_pips=_number(row, "Average_Outcome_Magnitude_Pips"),
        directional_state_ratio=_optional_number(row, "Directional_State_Ratio"),
        complex_consolidation_ratio=_optional_number(row, "Complex_Consolidation_Ratio"),
        volatile_rotation_ratio=_optional_number(row, "Volatile_Rotation_Ratio"),
        low_quality_rate=_optional_number(row, "Low_Quality_Rate"),
        unclassified_rate=_optional_number(row, "Unclassified_Rate"),
        has_directional_count_columns=_boolean(row, "__Has_Directional_Count_Columns"),
        has_complex_consolidation_count_column=_boolean(row, "__Has_Complex_Consolidation_Count_Column"),
        has_volatile_rotation_count_column=_boolean(row, "__Has_Volatile_Rotation_Count_Column"),
        has_low_quality_count_column=_boolean(row, "__Has_Low_Quality_Count_Column"),
        has_unclassified_count_column=_boolean(row, "__Has_Unclassified_Count_Column"),
    )


def _context_rows(rows: list[M15ValidationSummaryRow], timeframe: str) -> list[M15ValidationSummaryRow]:
    selected = [row for row in rows if row.timeframe == timeframe]
    return [row for row in selected if row.status in COMPLETED_STATUSES] or selected


def _context_interpretation(m5_rows: list[M15ValidationSummaryRow], h1_rows: list[M15ValidationSummaryRow]) -> str:
    if m5_rows and h1_rows:
        return "M15 context is available against M5 and H1 descriptive baselines."
    if m5_rows:
        return "M15 context is available against an M5 descriptive baseline."
    if h1_rows:
        return "M15 context is available against an H1 descriptive baseline."
    return "No M5/H1 context rows were available."


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


def _optional_number(row: pd.Series, column: str) -> float | None:
    value = _value(row, column, None)
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _boolean(row: pd.Series, column: str) -> bool:
    value = _value(row, column, False)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _value(row: pd.Series, column: str, default: Any) -> Any:
    actual = resolve_column([str(key) for key in row.index], column)
    if actual is None:
        return default
    return row[actual]


def _mean(values: list[int | float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
