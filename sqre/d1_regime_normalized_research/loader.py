"""Load D1 regime-normalized research inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.d1_regime_normalized_research.config import D1RegimeResearchConfig
from sqre.d1_regime_normalized_research.models import (
    D1RegimeScenarioData,
    D1RegimeScenarioInventoryRow,
    REQUIRED_SUMMARY_COLUMNS,
)
from sqre.d1_regime_normalized_research.regime_mapper import build_regime_lookup


def load_d1_regime_scenario_data(
    validation_summary_path: Path | str,
    validation_output_dir: Path | str,
    config: D1RegimeResearchConfig,
) -> list[D1RegimeScenarioData]:
    summary_path = Path(validation_summary_path)
    if not summary_path.exists():
        raise FileNotFoundError(f"D1 regime validation summary CSV not found: {summary_path}")

    frame = pd.read_csv(summary_path)
    frame = _canonicalize_summary_columns(frame, summary_path)
    output_dir = Path(validation_output_dir)
    regimes = build_regime_lookup(config)
    scenario_ids = set(regimes)
    rows: list[D1RegimeScenarioData] = []

    for _, row in frame.iterrows():
        scenario_id = text_value(row, "Scenario_ID")
        timeframe = text_value(row, "Timeframe").upper()
        if timeframe != "D1" or scenario_id not in scenario_ids:
            continue
        regime = regimes[scenario_id]
        scenario_dir = output_dir / scenario_id
        paths = _scenario_paths(scenario_dir)
        rows.append(
            D1RegimeScenarioData(
                inventory=D1RegimeScenarioInventoryRow(
                    scenario_id=scenario_id,
                    timeframe=timeframe,
                    status=text_value(row, "Status"),
                    regime_id=regime.regime_id,
                    regime_label=regime.regime_label,
                    ohlc_rows=integer_value(row, "OHLC_Rows"),
                    structures_detected=integer_value(row, "Structures_Detected"),
                    states_generated=integer_value(row, "States_Generated"),
                    unique_states=integer_value(row, "Unique_States"),
                    most_common_state=text_value(row, "Most_Common_State"),
                    average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
                    direction_alignment_rate=number_value(row, "Direction_Alignment_Rate"),
                    low_sample_conditions_research=integer_value(row, "Low_Sample_Conditions_Research"),
                    low_sample_conditions_price_outcome=integer_value(row, "Low_Sample_Conditions_Price_Outcome"),
                    price_outcome_summary_file_available=paths["price_outcome_summary"] is not None,
                    price_outcomes_file_available=paths["price_outcomes"] is not None,
                    market_states_file_available=paths["market_states"] is not None,
                    transitions_file_available=paths["transitions"] is not None,
                ),
                scenario_dir=scenario_dir,
                price_outcome_summary_path=paths["price_outcome_summary"],
                price_outcomes_path=paths["price_outcomes"],
                market_states_path=paths["market_states"],
                transitions_path=paths["transitions"],
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
        raise ValueError(f"Missing required D1 regime column(s) in {source_path}: {', '.join(missing)}")
    return frame.rename(columns=rename_map)


def _scenario_paths(scenario_dir: Path) -> dict[str, Path | None]:
    return {
        "price_outcome_summary": _first_existing(
            scenario_dir,
            [
                "research/condition_price_outcome_summary.csv",
                "condition_price_outcome_summary.csv",
                "data/research/condition_price_outcome_summary.csv",
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
    }


def _first_existing(root: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return path
    return None


def _resolve_index(row: pd.Series, target: str) -> str | None:
    return _resolve_column_name([str(column) for column in row.index], target)


def _resolve_column_name(columns: list[str], target: str) -> str | None:
    lookup = {_normalize(column): column for column in columns}
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
