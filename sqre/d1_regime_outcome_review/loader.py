"""Load D1 regime outcome review inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.d1_regime_outcome_review.models import ConditionProfileInput, REQUIRED_PROFILE_COLUMNS


NORMALIZED_PROFILES_FILE = "d1_regime_normalized_condition_profiles.csv"


def load_condition_profiles(input_dir: Path | str) -> list[ConditionProfileInput]:
    path = Path(input_dir) / NORMALIZED_PROFILES_FILE
    if not path.exists():
        raise FileNotFoundError(f"D1 normalized condition profiles file not found: {path}")
    frame = pd.read_csv(path)
    frame = _canonicalize_columns(frame, path)
    return [_profile_from_row(row) for _, row in frame.iterrows()]


def optional_input_file_status(input_dir: Path | str) -> dict[str, bool]:
    root = Path(input_dir)
    return {
        "scenario_inventory": (root / "d1_regime_scenario_inventory.csv").exists(),
        "condition_outcomes": (root / "d1_regime_condition_outcomes.csv").exists(),
        "state_outcome_profiles": (root / "d1_regime_state_outcome_profiles.csv").exists(),
        "transition_outcome_profiles": (root / "d1_regime_transition_outcome_profiles.csv").exists(),
        "research_summary": (root / "d1_regime_research_summary.csv").exists(),
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


def _profile_from_row(row: pd.Series) -> ConditionProfileInput:
    return ConditionProfileInput(
        condition_type=text_value(row, "Condition_Type"),
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        regime_count=integer_value(row, "Regime_Count"),
        regimes_present=text_value(row, "Regimes_Present"),
        scenario_count=integer_value(row, "Scenario_Count"),
        total_sample_size=integer_value(row, "Total_Sample_Size"),
        average_sample_size_per_regime=number_value(row, "Average_Sample_Size_Per_Regime"),
        average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
        average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
        average_direction_alignment_rate=number_value(row, "Average_Direction_Alignment_Rate"),
        forward_range_cv=number_value(row, "Forward_Range_CV"),
        outcome_magnitude_cv=number_value(row, "Outcome_Magnitude_CV"),
        direction_alignment_cv=number_value(row, "Direction_Alignment_CV"),
        regime_sensitivity_flag=text_value(row, "Regime_Sensitivity_Flag"),
    )


def _canonicalize_columns(frame: pd.DataFrame, source_path: Path) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    missing: list[str] = []
    columns = [str(column) for column in frame.columns]
    for required in REQUIRED_PROFILE_COLUMNS:
        actual = _resolve_column_name(columns, required)
        if actual is None:
            missing.append(required)
        elif actual != required:
            rename_map[actual] = required
    if missing:
        raise ValueError(f"Missing required D1 outcome review column(s) in {source_path}: {', '.join(missing)}")
    return frame.rename(columns=rename_map)


def _resolve_index(row: pd.Series, target: str) -> str | None:
    return _resolve_column_name([str(column) for column in row.index], target)


def _resolve_column_name(columns: list[str], target: str) -> str | None:
    lookup = {_normalize(column): column for column in columns}
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
