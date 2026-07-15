"""Load H4 state outcome deep dive inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.h4_state_outcome_deep_dive.models import (
    H4StateProfileInput,
    REQUIRED_PROFILE_COLUMNS,
    REQUIRED_SCENARIO_OUTCOME_COLUMNS,
    ScenarioOutcome,
)


PRICE_OUTCOME_PROFILES_FILE = "h4_d1_price_outcome_profiles.csv"
SCENARIO_OUTCOME_CANDIDATES = [
    Path("research/condition_price_outcome_summary.csv"),
    Path("condition_price_outcome_summary.csv"),
    Path("data/research/condition_price_outcome_summary.csv"),
]
H4_SCENARIOS = [
    "eurusd_h4_period_1",
    "eurusd_h4_period_2",
    "eurusd_h4_period_3",
    "eurusd_h4_period_4",
]
COLUMN_ALIASES = {
    "Condition_Type": [
        "Condition_Type",
        "condition_type",
    ],
    "Condition_Label": [
        "Condition_Label",
        "condition_label",
        "Condition_Value",
        "condition_value",
        "Condition",
        "condition",
        "State",
        "state",
        "Market_State",
        "market_state",
        "Condition_ID",
        "condition_id",
    ],
    "Forward_Window": [
        "Forward_Window",
        "forward_window",
        "Forward_Window_Candles",
        "forward_window_candles",
        "Forward_Candles",
        "forward_candles",
        "Window",
        "window",
    ],
    "Sample_Size": [
        "Sample_Size",
        "sample_size",
    ],
    "Average_Forward_Close_Return_Pips": [
        "Average_Forward_Close_Return_Pips",
        "average_forward_close_return_pips",
    ],
    "Median_Forward_Close_Return_Pips": [
        "Median_Forward_Close_Return_Pips",
        "median_forward_close_return_pips",
    ],
    "Average_Forward_Range_Pips": [
        "Average_Forward_Range_Pips",
        "average_forward_range_pips",
    ],
    "Average_Favorable_Displacement_Pips": [
        "Average_Favorable_Displacement_Pips",
        "average_favorable_displacement_pips",
        "Average_Max_Favorable_Displacement_Pips",
        "average_max_favorable_displacement_pips",
        "Max_Favorable_Displacement_Pips",
        "max_favorable_displacement_pips",
    ],
    "Average_Adverse_Displacement_Pips": [
        "Average_Adverse_Displacement_Pips",
        "average_adverse_displacement_pips",
        "Average_Max_Adverse_Displacement_Pips",
        "average_max_adverse_displacement_pips",
        "Max_Adverse_Displacement_Pips",
        "max_adverse_displacement_pips",
    ],
    "Average_Outcome_Magnitude_Pips": [
        "Average_Outcome_Magnitude_Pips",
        "average_outcome_magnitude_pips",
    ],
    "Direction_Alignment_Rate": [
        "Direction_Alignment_Rate",
        "direction_alignment_rate",
        "Average_Direction_Alignment_Rate",
        "average_direction_alignment_rate",
    ],
}


def load_price_outcome_profiles(h4_d1_research_dir: Path | str) -> list[H4StateProfileInput]:
    path = Path(h4_d1_research_dir) / PRICE_OUTCOME_PROFILES_FILE
    if not path.exists():
        raise FileNotFoundError(f"H4/D1 price outcome profiles file not found: {path}")
    frame = pd.read_csv(path)
    frame = _canonicalize_columns(frame, REQUIRED_PROFILE_COLUMNS, path)
    return [_profile_from_row(row) for _, row in frame.iterrows()]


def load_scenario_outcomes(validation_output_dir: Path | str) -> list[ScenarioOutcome]:
    root = Path(validation_output_dir)
    outcomes: list[ScenarioOutcome] = []
    for scenario_id in H4_SCENARIOS:
        scenario_dir = root / scenario_id
        outcome_path = find_scenario_outcome_file(scenario_dir)
        if outcome_path is None:
            continue
        frame = pd.read_csv(outcome_path)
        frame = _canonicalize_columns(frame, REQUIRED_SCENARIO_OUTCOME_COLUMNS, outcome_path)
        outcomes.extend(_scenario_outcome_from_row(row, scenario_id) for _, row in frame.iterrows())
    return outcomes


def find_scenario_outcome_file(scenario_dir: Path | str) -> Path | None:
    root = Path(scenario_dir)
    for candidate in SCENARIO_OUTCOME_CANDIDATES:
        path = root / candidate
        if path.exists():
            return path
    return None


def optional_input_file_status(h4_d1_research_dir: Path | str, validation_output_dir: Path | str) -> dict[str, bool]:
    research_root = Path(h4_d1_research_dir)
    validation_root = Path(validation_output_dir)
    status = {
        "h4_d1_state_research_profiles": (research_root / "h4_d1_state_research_profiles.csv").exists(),
        "h4_d1_timeframe_research_summary": (research_root / "h4_d1_timeframe_research_summary.csv").exists(),
        "h4_d1_scenario_inventory": (research_root / "h4_d1_scenario_inventory.csv").exists(),
    }
    for scenario_id in H4_SCENARIOS:
        status[f"{scenario_id}_condition_price_outcome_summary"] = find_scenario_outcome_file(
            validation_root / scenario_id
        ) is not None
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


def _profile_from_row(row: pd.Series) -> H4StateProfileInput:
    return H4StateProfileInput(
        timeframe=text_value(row, "Timeframe"),
        condition_type=text_value(row, "Condition_Type"),
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
        scenario_count=integer_value(row, "Scenario_Count"),
        scenarios_present=text_value(row, "Scenarios_Present"),
        total_sample_size=integer_value(row, "Total_Sample_Size"),
        average_sample_size_per_scenario=number_value(row, "Average_Sample_Size_Per_Scenario"),
        average_forward_close_return_pips=number_value(row, "Average_Forward_Close_Return_Pips"),
        median_forward_close_return_pips=number_value(row, "Median_Forward_Close_Return_Pips"),
        average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
        average_favorable_displacement_pips=number_value(row, "Average_Favorable_Displacement_Pips"),
        average_adverse_displacement_pips=number_value(row, "Average_Adverse_Displacement_Pips"),
        average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
        average_direction_alignment_rate=number_value(row, "Average_Direction_Alignment_Rate"),
        forward_range_cv=number_value(row, "Forward_Range_CV"),
        outcome_magnitude_cv=number_value(row, "Outcome_Magnitude_CV"),
        scenario_sensitivity_flag=text_value(row, "Scenario_Sensitivity_Flag"),
        sample_adequacy_flag=text_value(row, "Sample_Adequacy_Flag"),
        outcome_profile_diagnostic=text_value(row, "Outcome_Profile_Diagnostic"),
    )


def _scenario_outcome_from_row(row: pd.Series, scenario_id: str) -> ScenarioOutcome:
    return ScenarioOutcome(
        scenario_id=scenario_id,
        timeframe=text_value(row, "Timeframe", "H4"),
        condition_type=text_value(row, "Condition_Type"),
        condition_label=text_value(row, "Condition_Label"),
        forward_window=integer_value(row, "Forward_Window"),
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
        raise ValueError(f"Missing required H4 state deep dive column(s) in {source_path}: {', '.join(missing)}")
    return frame.rename(columns=rename_map)


def _resolve_index(row: pd.Series, target: str) -> str | None:
    return _resolve_column_name([str(column) for column in row.index], target)


def _resolve_column_name(columns: list[str], target: str) -> str | None:
    lookup = {_normalize(column): column for column in columns}
    for alias in COLUMN_ALIASES.get(target, [target]):
        actual = lookup.get(_normalize(alias))
        if actual is not None:
            return actual
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
