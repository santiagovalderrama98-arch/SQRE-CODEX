"""CSV loading helpers for H4/D1 contextual transition review."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas.errors import EmptyDataError

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.models import SourceInventoryRow


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


def text_value(row: pd.Series | None, aliases: Iterable[str], default: str = "") -> str:
    if row is None:
        return default
    raw = value(row, aliases, default)
    if pd.isna(raw):
        return default
    return str(raw).strip()


def int_value(row: pd.Series | None, aliases: Iterable[str], default: int = 0) -> int:
    raw = value(row, aliases, default) if row is not None else default
    try:
        if pd.isna(raw):
            return default
        return int(round(float(raw)))
    except (TypeError, ValueError):
        return default


def first_row(frame: pd.DataFrame) -> pd.Series | None:
    if frame.empty:
        return None
    return frame.iloc[0]


def first_existing_frame(directory: Path, filenames: Iterable[str]) -> tuple[Path, pd.DataFrame]:
    fallback = directory / next(iter(filenames))
    for filename in filenames:
        path = directory / filename
        frame = read_optional_csv(path)
        if path.exists():
            return path, frame
    return fallback, pd.DataFrame()


def source_inventory_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    frame = read_optional_csv(path)
    if not path.exists():
        return SourceInventoryRow(source_name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    if frame.empty:
        return SourceInventoryRow(source_name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(source_name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")


def build_source_inventory(config: H4D1ContextualTransitionReviewConfig) -> list[SourceInventoryRow]:
    files = [
        ("h4_context_inventory", "H4_COMBINED_CONTEXT", config.h4_combined_context_dir / "h4_transition_state_context_inventory.csv"),
        ("h4_context_interpretation", "H4_COMBINED_CONTEXT", config.h4_combined_context_dir / "h4_transition_state_context_interpretation_matrix.csv"),
        ("h4_context_summary", "H4_COMBINED_CONTEXT", config.h4_combined_context_dir / "h4_transition_state_combined_context_summary.csv"),
        ("d1_regime_normalized_summary", "D1_REGIME_NORMALIZED", config.d1_regime_normalized_dir / "d1_regime_normalized_summary.csv"),
        ("d1_regime_outcome_review_summary", "D1_REGIME_OUTCOME", config.d1_regime_outcome_review_dir / "d1_regime_outcome_review_summary.csv"),
        ("d1_state_deep_dive_inventory", "D1_STATE_DEEP_DIVE", config.d1_state_deep_dive_dir / "d1_state_deep_dive_profile_inventory.csv"),
        ("h4_d1_structural_research_summary", "H4_D1_STRUCTURAL_RESEARCH", config.h4_d1_structural_research_dir / "h4_d1_structural_research_summary.csv"),
        ("h4_d1_validation_summary", "H4_D1_VALIDATION", config.h4_d1_validation_dir / "multi_scenario_validation_summary.csv"),
        ("partial_complementary_summary", "PARTIAL_CONTEXT", config.partial_complement_dir / "h4_partial_complementary_dispersion_summary.csv"),
        ("partial_validation_summary", "PARTIAL_VALIDATION", config.partial_validation_dir / "h4_partial_validation_run_summary.csv"),
    ]
    return [source_inventory_row(name, source_type, path) for name, source_type, path in files]


CONTEXT_ID_ALIASES = ["Context_ID", "context_id"]
SOURCE_STATE_ALIASES = ["Source_State", "From_State", "Previous_State", "State_From"]
TARGET_STATE_ALIASES = ["Target_State", "To_State", "Next_State", "State_To"]
TRANSITION_LABEL_ALIASES = ["Transition_Label", "Transition", "Condition_Label", "Condition_Value"]
FORWARD_WINDOW_ALIASES = ["Forward_Window", "Forward_Window_Candles", "FW"]
H4_INTERPRETATION_ALIASES = [
    "Combined_Context_Interpretation_Class",
    "Context_Interpretation_Class",
    "Dominant_Combined_Context_Interpretation",
]
H4_READINESS_ALIASES = ["Combined_Context_Readiness_Flag", "H4_Transition_State_Context_Readiness_Flag", "Readiness_Flag"]
H4_DISPERSION_ALIASES = ["Combined_Dispersion_Class", "H4_Transition_State_Context_Profile"]
H4_SENSITIVITY_ALIASES = ["Combined_Sensitivity_Class"]
SCENARIO_ID_ALIASES = ["Scenario_ID", "scenario_id", "Validation_Scenario_ID", "Sample_ID", "Period_ID"]
REGIME_LABEL_ALIASES = ["Regime_Label", "D1_Regime_Label", "Regime", "Scenario_Regime", "Regime_ID"]
STATE_LABEL_ALIASES = ["State_Label", "Condition_Label", "Condition_Value", "Market_State", "State"]
D1_STATE_PROFILE_ALIASES = ["D1_State_Profile", "State_Profile", "Profile_Type"]
D1_DISPERSION_ALIASES = [
    "Outcome_Dispersion_Class",
    "Profile_Dispersion_Class",
    "D1_Outcome_Dispersion_Class",
    "Regime_Sensitivity_Class",
]
SAMPLE_ADEQUACY_ALIASES = [
    "Sample_Adequacy_Class",
    "Profile_Research_Readiness_Class",
    "Research_Readiness_Flag",
    "D1_Research_Readiness_Flag",
]
READINESS_ALIASES = ["Readiness_Flag", "D1_Outcome_Review_Readiness_Flag", "Research_Readiness_Flag"]
START_DATE_ALIASES = ["Start_Date", "Scenario_Start", "Period_Start", "From_Date"]
END_DATE_ALIASES = ["End_Date", "Scenario_End", "Period_End", "To_Date"]
