"""CSV helpers for H4 transition/state combined context review."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas.errors import EmptyDataError

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(resolved)
    except EmptyDataError:
        return pd.DataFrame()


def resolve_column(frame: pd.DataFrame, aliases: Iterable[str]) -> str | None:
    lookup = {str(column).strip().lower(): str(column) for column in frame.columns}
    for alias in aliases:
        column = lookup.get(str(alias).strip().lower())
        if column is not None:
            return column
    return None


def value(row: pd.Series, aliases: Iterable[str], default: object = "") -> object:
    lookup = {str(column).strip().lower(): column for column in row.index}
    for alias in aliases:
        column = lookup.get(str(alias).strip().lower())
        if column is None:
            continue
        raw = row.get(column)
        if pd.isna(raw):
            return default
        return raw
    return default


def text_value(row: pd.Series, aliases: Iterable[str], default: str = "") -> str:
    raw = value(row, aliases, default)
    if pd.isna(raw):
        return default
    return str(raw).strip()


def number_value(row: pd.Series, aliases: Iterable[str], default: float = 0.0) -> float:
    raw = value(row, aliases, default)
    try:
        if pd.isna(raw):
            return default
        return float(raw)
    except (TypeError, ValueError):
        return default


def int_value(row: pd.Series, aliases: Iterable[str], default: int = 0) -> int:
    return int(round(number_value(row, aliases, float(default))))


def first_row(frame: pd.DataFrame) -> pd.Series | None:
    if frame.empty:
        return None
    return frame.iloc[0]


def read_first_summary_row(directory: Path) -> pd.Series | None:
    for path in sorted(directory.glob("*summary.csv")):
        row = first_row(read_optional_csv(path))
        if row is not None:
            return row
    return None


def read_first_existing_row(directory: Path, filenames: Iterable[str]) -> pd.Series | None:
    for filename in filenames:
        row = first_row(read_optional_csv(directory / filename))
        if row is not None:
            return row
    return None


def first_existing_path(directory: Path, filenames: Iterable[str]) -> Path:
    for filename in filenames:
        path = directory / filename
        if path.exists():
            return path
    return directory / next(iter(filenames))


def source_inventory_row(source_name: str, source_type: str, path: Path):
    frame = read_optional_csv(path)
    if not path.exists():
        status, rows, diagnostic = "MISSING", 0, "Source file was not found."
    elif frame.empty:
        status, rows, diagnostic = "EMPTY", 0, "Source file was found but has no data rows."
    else:
        status, rows, diagnostic = "LOADED", len(frame), "Source file loaded."
    from sqre.h4_transition_state_combined_context_review.models import SourceInventoryRow

    return SourceInventoryRow(source_name, source_type, str(path), path.exists(), status, rows, diagnostic)


def build_source_inventory(config: H4TransitionStateCombinedContextReviewConfig):
    state_sensitive_path = first_existing_path(
        config.h4_state_sensitive_dir,
        STATE_SENSITIVE_FILENAMES,
    )
    files = [
        ("state_deep_dive_profile_inventory", "STATE_DEEP_DIVE", config.h4_state_deep_dive_dir / "h4_state_deep_dive_profile_inventory.csv"),
        ("state_deep_dive_summary", "STATE_DEEP_DIVE", config.h4_state_deep_dive_dir / "h4_state_deep_dive_summary.csv"),
        ("state_dispersion_summary", "STATE_DISPERSION", config.h4_state_dispersion_dir / "h4_scenario_dispersion_review_summary.csv"),
        ("state_sensitive_summary", "STATE_SENSITIVITY", state_sensitive_path),
        ("transition_deep_dive_profile_inventory", "TRANSITION_DEEP_DIVE", config.h4_transition_deep_dive_dir / "h4_transition_deep_dive_profile_inventory.csv"),
        ("transition_outcome_statistics", "TRANSITION_DEEP_DIVE", config.h4_transition_deep_dive_dir / "h4_transition_outcome_statistics.csv"),
        ("transition_dispersion_summary", "TRANSITION_DISPERSION", config.h4_transition_dispersion_dir / "h4_transition_scenario_dispersion_review_summary.csv"),
        ("transition_sensitive_profile_review", "TRANSITION_SENSITIVITY", config.h4_transition_sensitive_dir / "h4_transition_scenario_sensitive_profile_review.csv"),
        ("transition_sensitive_summary", "TRANSITION_SENSITIVITY", config.h4_transition_sensitive_dir / "h4_transition_scenario_sensitive_review_summary.csv"),
        ("partial_baseline_interpretation", "PARTIAL_CONTEXT", config.partial_complement_dir / "h4_partial_baseline_interpretation_matrix.csv"),
        ("partial_sample_caveat", "PARTIAL_CONTEXT", config.partial_complement_dir / "h4_partial_sample_caveat_review.csv"),
        ("partial_complementary_summary", "PARTIAL_CONTEXT", config.partial_complement_dir / "h4_partial_complementary_dispersion_summary.csv"),
        ("partial_validation_summary", "PARTIAL_VALIDATION", config.partial_validation_dir / "h4_partial_validation_run_summary.csv"),
    ]
    return [source_inventory_row(name, source_type, path) for name, source_type, path in files]


TRANSITION_LABEL_ALIASES = ["Transition_Label", "Transition", "transition", "Transition_Name", "Condition_Label", "Condition_Value"]
SOURCE_STATE_ALIASES = ["Source_State", "From_State", "Previous_State", "State_From"]
TARGET_STATE_ALIASES = ["Target_State", "To_State", "Next_State", "State_To"]
FORWARD_WINDOW_ALIASES = ["Forward_Window", "Forward_Window_Candles", "forward_window", "FW"]
SAMPLE_SIZE_ALIASES = ["Sample_Size", "sample_size", "Condition_Count", "condition_count", "Transition_Count", "State_Count"]
DISPERSION_ALIASES = [
    "Profile_Dispersion_Class",
    "Dispersion_Class",
    "Outcome_Dispersion_Class",
    "Dominant_Dispersion_Class",
    "Dispersion_Driver_Class",
    "H4_Dispersion_Profile",
    "H4_Transition_Dispersion_Profile",
    "Sensitivity_Class",
    "H4_Scenario_Sensitive_Profile",
    "H4_Transition_Scenario_Sensitive_Profile",
    "Profile_Research_Readiness_Class",
    "Transition_Profile_Readiness_Class",
]
READINESS_ALIASES = [
    "Readiness_Flag",
    "H4_Aggregation_Readiness_Flag",
    "H4_Review_Readiness_Flag",
    "H4_Transition_Aggregation_Readiness_Flag",
    "H4_Transition_Scenario_Sensitive_Review_Diagnostic",
    "Profile_Research_Readiness_Class",
    "Transition_Profile_Readiness_Class",
    "Profile_Readiness_Class",
    "Sample_Adequacy_Class",
]

STATE_SENSITIVE_FILENAMES = [
    "h4_scenario_sensitive_state_review_summary.csv",
    "h4_scenario_sensitive_review_summary.csv",
    "h4_scenario_sensitive_state_profile_review.csv",
    "h4_scenario_sensitive_profile_review.csv",
]

STATE_DISPERSION_FILENAMES = [
    "h4_profile_dispersion_diagnostics.csv",
    "h4_scenario_sensitive_profiles.csv",
    "h4_sample_constrained_profiles.csv",
    "h4_state_dispersion_summary.csv",
    "h4_scenario_dispersion_review_summary.csv",
]

TRANSITION_DISPERSION_FILENAMES = [
    "h4_transition_profile_dispersion_diagnostics.csv",
    "h4_transition_scenario_sensitive_profiles.csv",
    "h4_transition_sample_constrained_profiles.csv",
    "h4_transition_source_state_dispersion_summary.csv",
    "h4_transition_target_state_dispersion_summary.csv",
    "h4_transition_scenario_dispersion_review_summary.csv",
]
