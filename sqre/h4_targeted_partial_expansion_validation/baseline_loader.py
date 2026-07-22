"""Baseline metric loader for H4 targeted partial expansion validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_targeted_partial_expansion_validation.loader import (
    mean_column,
    read_optional_csv,
    resolve_column,
)
from sqre.h4_targeted_partial_expansion_validation.models import BaselineMetrics


def load_baseline_metrics(
    validation_dir: Path | str,
    research_dir: Path | str,
    *,
    timeframe: str = "H4",
) -> BaselineMetrics:
    validation = read_optional_csv(Path(validation_dir) / "h4_d1_validation_summary.csv")
    h4_validation = _filter_timeframe(validation, timeframe)
    h4_validation = _exclude_partial(h4_validation)

    scenario_count = _scenario_count(h4_validation)
    return BaselineMetrics(
        scenario_count=scenario_count,
        average_ohlc_rows=round(mean_column(h4_validation, ["OHLC_Rows", "ohlc_rows"]), 4),
        average_structure_count=round(mean_column(h4_validation, ["Structure_Count", "structure_count"]), 4),
        average_state_count=round(mean_column(h4_validation, ["State_Count", "state_count"]), 4),
        average_transition_count=round(mean_column(h4_validation, ["Transition_Count", "transition_count"]), 4),
        average_forward_range_pips=round(_mean_research_metric(Path(research_dir), "forward_range"), 4),
        average_outcome_magnitude_pips=round(_mean_research_metric(Path(research_dir), "outcome_magnitude"), 4),
    )


def _filter_timeframe(frame: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if frame.empty:
        return frame
    column = resolve_column(frame, ["Timeframe", "timeframe"])
    if column is None:
        return frame
    return frame[frame[column].astype(str).str.upper() == timeframe.upper()]


def _exclude_partial(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    scenario_column = resolve_column(frame, ["Scenario_ID", "scenario_id", "Scenario", "scenario"])
    if scenario_column is None:
        return frame
    return frame[~frame[scenario_column].astype(str).str.lower().str.contains("partial")]


def _scenario_count(frame: pd.DataFrame) -> int:
    if frame.empty:
        return 0
    scenario_column = resolve_column(frame, ["Scenario_ID", "scenario_id", "Scenario", "scenario"])
    if scenario_column:
        return int(frame[scenario_column].nunique())
    return len(frame)


def _mean_research_metric(research_dir: Path, metric: str) -> float:
    if not research_dir.exists():
        return 0.0
    aliases = (
        ["Average_Forward_Range_Pips", "average_forward_range_pips"]
        if metric == "forward_range"
        else ["Average_Outcome_Magnitude_Pips", "average_outcome_magnitude_pips"]
    )
    values: list[float] = []
    for path in sorted(research_dir.rglob("*.csv")):
        frame = read_optional_csv(path)
        column = resolve_column(frame, aliases)
        timeframe_column = resolve_column(frame, ["Timeframe", "timeframe"])
        if column is None:
            continue
        scoped = frame
        if timeframe_column is not None:
            scoped = frame[frame[timeframe_column].astype(str).str.upper() == "H4"]
        series = pd.to_numeric(scoped[column], errors="coerce").dropna()
        values.extend(float(value) for value in series)
    if not values:
        return 0.0
    return sum(values) / len(values)
