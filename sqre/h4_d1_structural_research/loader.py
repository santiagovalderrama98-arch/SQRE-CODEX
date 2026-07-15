"""Load H4/D1 structural research inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.h4_d1_structural_research.models import (
    REQUIRED_SUMMARY_COLUMNS,
    ScenarioData,
    ScenarioInventoryRow,
)


INCLUDED_TIMEFRAMES = {"H4", "D1"}


def load_h4_d1_scenario_data(
    validation_summary_path: Path | str,
    validation_output_dir: Path | str,
) -> list[ScenarioData]:
    summary_path = Path(validation_summary_path)
    if not summary_path.exists():
        raise FileNotFoundError(f"H4/D1 validation summary CSV not found: {summary_path}")

    frame = pd.read_csv(summary_path)
    frame = _canonicalize_summary_columns(frame, summary_path)
    output_dir = Path(validation_output_dir)
    rows: list[ScenarioData] = []
    for _, row in frame.iterrows():
        timeframe = _text(row, "Timeframe").upper()
        if timeframe not in INCLUDED_TIMEFRAMES:
            continue
        scenario_id = _text(row, "Scenario_ID")
        scenario_dir = output_dir / scenario_id
        paths = _scenario_paths(scenario_dir)
        rows.append(
            ScenarioData(
                inventory=ScenarioInventoryRow(
                    scenario_id=scenario_id,
                    timeframe=timeframe,
                    status=_text(row, "Status"),
                    ohlc_rows=_integer(row, "OHLC_Rows"),
                    structures_detected=_integer(row, "Structures_Detected"),
                    states_generated=_integer(row, "States_Generated"),
                    unique_states=_integer(row, "Unique_States"),
                    most_common_state=_text(row, "Most_Common_State"),
                    average_forward_range_pips=_number(row, "Average_Forward_Range_Pips"),
                    direction_alignment_rate=_number(row, "Direction_Alignment_Rate"),
                    low_sample_conditions_research=_integer(row, "Low_Sample_Conditions_Research"),
                    low_sample_conditions_price_outcome=_integer(row, "Low_Sample_Conditions_Price_Outcome"),
                    market_states_file_available=paths["market_states"] is not None,
                    transitions_file_available=paths["transitions"] is not None,
                    condition_summaries_file_available=paths["condition_summaries"] is not None,
                    price_outcomes_file_available=paths["price_outcomes"] is not None,
                    price_outcome_summary_file_available=paths["price_outcome_summary"] is not None,
                    sequence_outcomes_file_available=paths["sequence_outcomes"] is not None,
                ),
                scenario_dir=scenario_dir,
                market_states_path=paths["market_states"],
                transitions_path=paths["transitions"],
                condition_summaries_path=paths["condition_summaries"],
                forward_state_distributions_path=paths["forward_state_distributions"],
                forward_transition_distributions_path=paths["forward_transition_distributions"],
                sequence_outcomes_path=paths["sequence_outcomes"],
                price_outcomes_path=paths["price_outcomes"],
                price_outcome_summary_path=paths["price_outcome_summary"],
            )
        )
    return rows


def read_csv(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def resolve_column(frame: pd.DataFrame, target: str) -> str | None:
    lookup = {_normalize(column): str(column) for column in frame.columns}
    return lookup.get(_normalize(target))


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


def _canonicalize_summary_columns(frame: pd.DataFrame, source_path: Path) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    missing: list[str] = []
    columns = [str(column) for column in frame.columns]
    for required in REQUIRED_SUMMARY_COLUMNS:
        actual = _resolve_column_name(columns, required)
        if actual is None:
            missing.append(required)
        elif actual != required:
            rename_map[actual] = required
    if missing:
        raise ValueError(f"Missing required H4/D1 research column(s) in {source_path}: {', '.join(missing)}")
    return frame.rename(columns=rename_map)


def _scenario_paths(scenario_dir: Path) -> dict[str, Path | None]:
    return {
        "market_states": _first_existing(
            scenario_dir,
            [
                "processed/market_states.csv",
                "market_states.csv",
                "data/processed/market_states.csv",
            ],
        ),
        "transitions": _first_existing(
            scenario_dir,
            [
                "processed/state_transitions.csv",
                "state_transitions.csv",
                "data/processed/state_transitions.csv",
            ],
        ),
        "condition_summaries": _first_existing(
            scenario_dir,
            [
                "research/condition_summaries.csv",
                "condition_summaries.csv",
                "data/research/condition_summaries.csv",
            ],
        ),
        "forward_state_distributions": _first_existing(
            scenario_dir,
            [
                "research/forward_state_distributions.csv",
                "forward_state_distributions.csv",
                "data/research/forward_state_distributions.csv",
            ],
        ),
        "forward_transition_distributions": _first_existing(
            scenario_dir,
            [
                "research/forward_transition_distributions.csv",
                "forward_transition_distributions.csv",
                "data/research/forward_transition_distributions.csv",
            ],
        ),
        "sequence_outcomes": _first_existing(
            scenario_dir,
            [
                "research/sequence_outcomes.csv",
                "sequence_outcomes.csv",
                "data/research/sequence_outcomes.csv",
            ],
        ),
        "price_outcomes": _first_existing(
            scenario_dir,
            [
                "research/price_outcomes.csv",
                "price_outcomes.csv",
                "data/research/price_outcomes.csv",
            ],
        ),
        "price_outcome_summary": _first_existing(
            scenario_dir,
            [
                "research/condition_price_outcome_summary.csv",
                "condition_price_outcome_summary.csv",
                "data/research/condition_price_outcome_summary.csv",
            ],
        ),
    }


def _first_existing(root: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return path
    return None


def _text(row: pd.Series, column: str) -> str:
    return text_value(row, column)


def _integer(row: pd.Series, column: str) -> int:
    return integer_value(row, column)


def _number(row: pd.Series, column: str) -> float:
    return number_value(row, column)


def _resolve_index(row: pd.Series, target: str) -> str | None:
    return _resolve_column_name([str(column) for column in row.index], target)


def _resolve_column_name(columns: list[str], target: str) -> str | None:
    lookup = {_normalize(column): column for column in columns}
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
