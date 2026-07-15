"""Load D1 state outcome deep dive inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.d1_state_outcome_deep_dive.models import (
    REQUIRED_OUTCOME_COLUMNS,
    REQUIRED_PROFILE_COLUMNS,
    RegimeOutcome,
    StateProfile,
)


RESEARCH_READY_FILE = "d1_research_ready_condition_profiles.csv"
REGIME_SENSITIVE_FILE = "d1_regime_sensitive_condition_profiles.csv"
REGIME_OUTCOMES_FILE = "d1_regime_condition_outcomes.csv"


def load_research_ready_profiles(outcome_review_dir: Path | str) -> list[StateProfile]:
    path = Path(outcome_review_dir) / RESEARCH_READY_FILE
    return _load_profiles(path, "RESEARCH_READY", required=True)


def load_regime_sensitive_profiles(outcome_review_dir: Path | str) -> list[StateProfile]:
    path = Path(outcome_review_dir) / REGIME_SENSITIVE_FILE
    return _load_profiles(path, "REGIME_SENSITIVE_OBSERVATION", required=False)


def load_regime_outcomes(regime_research_dir: Path | str) -> list[RegimeOutcome]:
    path = Path(regime_research_dir) / REGIME_OUTCOMES_FILE
    if not path.exists():
        raise FileNotFoundError(f"D1 regime condition outcomes file not found: {path}")
    frame = pd.read_csv(path)
    frame = _canonicalize_columns(frame, REQUIRED_OUTCOME_COLUMNS, path)
    return [_outcome_from_row(row) for _, row in frame.iterrows()]


def optional_input_file_status(outcome_review_dir: Path | str, regime_research_dir: Path | str) -> dict[str, bool]:
    review_root = Path(outcome_review_dir)
    regime_root = Path(regime_research_dir)
    return {
        "d1_regime_sensitive_condition_profiles": (review_root / REGIME_SENSITIVE_FILE).exists(),
        "d1_state_condition_quality_summary": (review_root / "d1_state_condition_quality_summary.csv").exists(),
        "d1_condition_quality_inventory": (review_root / "d1_condition_quality_inventory.csv").exists(),
        "d1_regime_outcome_review_summary": (review_root / "d1_regime_outcome_review_summary.csv").exists(),
        "d1_regime_state_outcome_profiles": (regime_root / "d1_regime_state_outcome_profiles.csv").exists(),
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


def _load_profiles(path: Path, profile_type: str, required: bool) -> list[StateProfile]:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"D1 state profile file not found: {path}")
        return []
    frame = pd.read_csv(path)
    frame = _canonicalize_columns(frame, REQUIRED_PROFILE_COLUMNS, path)
    return [_profile_from_row(row, profile_type) for _, row in frame.iterrows()]


def _profile_from_row(row: pd.Series, profile_type: str) -> StateProfile:
    return StateProfile(
        condition_type=text_value(row, "Condition_Type"),
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        profile_type=profile_type,
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
        sample_adequacy_class=text_value(row, "Sample_Adequacy_Class"),
        regime_coverage_class=text_value(row, "Regime_Coverage_Class"),
        dispersion_class=text_value(row, "Dispersion_Class"),
        sensitivity_class=text_value(row, "Sensitivity_Class"),
        condition_research_class=text_value(row, "Condition_Research_Class"),
        profile_diagnostic=text_value(row, "Condition_Review_Diagnostic"),
        recommended_follow_up=text_value(row, "Recommended_Follow_Up"),
    )


def _outcome_from_row(row: pd.Series) -> RegimeOutcome:
    return RegimeOutcome(
        condition_type=text_value(row, "Condition_Type"),
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        regime_id=text_value(row, "Regime_ID"),
        regime_label=text_value(row, "Regime_Label"),
        scenario_id=text_value(row, "Scenario_ID"),
        timeframe=text_value(row, "Timeframe"),
        sample_size=integer_value(row, "Sample_Size"),
        average_forward_close_return_pips=number_value(row, "Average_Forward_Close_Return_Pips"),
        median_forward_close_return_pips=number_value(row, "Median_Forward_Close_Return_Pips"),
        average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
        average_favorable_displacement_pips=number_value(row, "Average_Favorable_Displacement_Pips"),
        average_adverse_displacement_pips=number_value(row, "Average_Adverse_Displacement_Pips"),
        average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
        direction_alignment_rate=number_value(row, "Direction_Alignment_Rate"),
        sample_adequacy_flag=text_value(row, "Sample_Adequacy_Flag"),
    )


def _canonicalize_columns(frame: pd.DataFrame, required_columns: list[str], source_path: Path) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    missing: list[str] = []
    columns = [str(column) for column in frame.columns]
    for required in required_columns:
        actual = _resolve_column_name(columns, required)
        if actual is None:
            missing.append(required)
        elif actual != required:
            rename_map[actual] = required
    if missing:
        raise ValueError(f"Missing required D1 state deep dive column(s) in {source_path}: {', '.join(missing)}")
    return frame.rename(columns=rename_map)


def _resolve_index(row: pd.Series, target: str) -> str | None:
    return _resolve_column_name([str(column) for column in row.index], target)


def _resolve_column_name(columns: list[str], target: str) -> str | None:
    lookup = {_normalize(column): column for column in columns}
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
