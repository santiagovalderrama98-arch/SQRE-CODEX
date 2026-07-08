"""Metric extraction for calibration experiment outputs."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.calibration_experiments.models import ExperimentMetricsRow, ExperimentRun, ExperimentRunResult


STATE_TYPES = [
    "DIRECTIONAL_DISPLACEMENT",
    "DIRECTIONAL_EXPANSION",
    "DIRECTIONAL_DRIFT",
    "VOLATILE_ROTATION",
    "COMPLEX_CONSOLIDATION",
    "NEUTRAL_COMPRESSION",
    "LOW_QUALITY_STRUCTURE",
    "UNCLASSIFIED",
]


def collect_experiment_metrics(
    experiment_run: ExperimentRun,
    result: ExperimentRunResult,
) -> ExperimentMetricsRow:
    ohlc = _read_csv_if_exists(experiment_run.ohlc_path)
    structures = _read_csv_if_exists(experiment_run.processed_dir / "structures.csv")
    states = _read_csv_if_exists(experiment_run.processed_dir / "market_states.csv")
    transitions = _read_csv_if_exists(experiment_run.processed_dir / "state_transitions.csv")
    condition_summaries = _read_csv_if_exists(experiment_run.research_dir / "condition_summaries.csv")
    price_outcomes = _read_csv_if_exists(experiment_run.research_dir / "price_outcomes.csv")
    price_summary = _read_csv_if_exists(experiment_run.research_dir / "condition_price_outcome_summary.csv")
    price_distribution = _read_csv_if_exists(experiment_run.research_dir / "price_outcome_distributions.csv")

    period_start, period_end = _period_from_ohlc(ohlc)
    state_counts = _counts(states, "Market_State")
    states_generated = len(states)
    conditions_evaluated = _conditions_evaluated(condition_summaries)
    condition_summary_rows = len(condition_summaries)
    low_sample_research = _low_sample_count(condition_summaries)
    price_summary_rows = len(price_summary)
    low_sample_price = _low_sample_count(price_summary)
    structures_detected = len(structures)
    average_structure_duration = _mean(structures, "Duration_Seconds")

    return ExperimentMetricsRow(
        experiment_run_id=experiment_run.experiment_run_id,
        experiment_type=experiment_run.experiment_type,
        experiment_id=experiment_run.experiment_id,
        scenario_id=experiment_run.scenario_id,
        symbol=experiment_run.symbol,
        timeframe=experiment_run.timeframe,
        status=result.status,
        message=result.message,
        period_start=period_start,
        period_end=period_end,
        ohlc_rows=len(ohlc),
        max_structure_duration_seconds=experiment_run.max_structure_duration_seconds,
        minimum_sample_size=experiment_run.minimum_sample_size,
        forward_windows=",".join(str(item) for item in experiment_run.forward_candles),
        structures_detected=structures_detected,
        average_structure_duration=average_structure_duration,
        duration_utilization_ratio=_safe_ratio(
            average_structure_duration,
            experiment_run.max_structure_duration_seconds,
        ),
        average_price_displacement=_mean(structures, "Price_Displacement"),
        most_common_direction=_mode(structures, "Direction"),
        average_persistence_index=_mean(structures, "Persistence_Index"),
        average_structural_complexity=_mean(structures, "Structural_Complexity"),
        average_structural_stability=_mean(structures, "Structural_Stability"),
        average_structural_confidence=_mean(structures, "Structural_Confidence"),
        states_generated=states_generated,
        unique_states=_unique(states, "Market_State"),
        most_common_state=_mode(states, "Market_State"),
        most_common_state_ratio=_safe_ratio(_most_common_state_count(state_counts), states_generated),
        directional_state_ratio=_safe_ratio(
            state_counts.get("DIRECTIONAL_DISPLACEMENT", 0)
            + state_counts.get("DIRECTIONAL_EXPANSION", 0)
            + state_counts.get("DIRECTIONAL_DRIFT", 0),
            states_generated,
        ),
        compression_consolidation_ratio=_safe_ratio(
            state_counts.get("COMPLEX_CONSOLIDATION", 0)
            + state_counts.get("NEUTRAL_COMPRESSION", 0),
            states_generated,
        ),
        volatile_rotation_ratio=_safe_ratio(state_counts.get("VOLATILE_ROTATION", 0), states_generated),
        unclassified_rate=_safe_ratio(state_counts.get("UNCLASSIFIED", 0), states_generated),
        low_quality_rate=_safe_ratio(state_counts.get("LOW_QUALITY_STRUCTURE", 0), states_generated),
        average_state_confidence=_mean(states, "State_Confidence"),
        transitions_generated=len(transitions),
        unique_transitions=_unique(transitions, "Transition_Label"),
        most_common_transition=_mode(transitions, "Transition_Label"),
        state_change_rate=_boolean_rate(transitions, "State_Changed"),
        direction_change_rate=_boolean_rate(transitions, "Direction_Changed"),
        average_transition_magnitude=_mean(transitions, "Transition_Magnitude"),
        average_transition_stability=_mean(transitions, "Transition_Stability"),
        conditions_evaluated=conditions_evaluated,
        condition_summary_rows=condition_summary_rows,
        low_sample_conditions_research=low_sample_research,
        research_low_sample_rate=_safe_ratio(low_sample_research, conditions_evaluated),
        price_outcomes_generated=len(price_outcomes),
        price_outcome_summary_rows=price_summary_rows,
        price_outcome_distribution_rows=len(price_distribution),
        low_sample_conditions_price_outcome=low_sample_price,
        price_outcome_low_sample_rate=_safe_ratio(low_sample_price, price_summary_rows),
        average_forward_close_return_pips=_mean(price_summary, "Average_Forward_Close_Return_Pips"),
        median_forward_close_return_pips=_mean(price_summary, "Median_Forward_Close_Return_Pips"),
        average_forward_range_pips=_mean(price_summary, "Average_Forward_Range_Pips"),
        average_outcome_magnitude_pips=_mean(price_summary, "Average_Outcome_Magnitude_Pips"),
        direction_alignment_rate=_mean(price_summary, "Direction_Alignment_Rate"),
        experiment_notes=_notes(result.status),
    )


def apply_baseline_comparisons(rows: Iterable[ExperimentMetricsRow]) -> list[ExperimentMetricsRow]:
    items = list(rows)
    baselines = {
        ("DURATION", row.scenario_id): row
        for row in items
        if row.experiment_type == "DURATION" and row.experiment_id == "duration_baseline"
    }
    baselines.update(
        {
            ("SAMPLE_SIZE", row.scenario_id): row
            for row in items
            if row.experiment_type == "SAMPLE_SIZE" and row.experiment_id == "sample_size_5"
        }
    )
    return [_with_comparison(row, baselines.get((row.experiment_type, row.scenario_id))) for row in items]


def _with_comparison(row: ExperimentMetricsRow, baseline: ExperimentMetricsRow | None) -> ExperimentMetricsRow:
    if baseline is None:
        return row
    structure_change = _relative_change(row.structures_detected, baseline.structures_detected)
    duration_change = _relative_change(row.average_structure_duration, baseline.average_structure_duration)
    diversity_change = _relative_change(row.unique_states, baseline.unique_states)
    range_change = _relative_change(row.average_forward_range_pips, baseline.average_forward_range_pips)
    return replace(
        row,
        relative_structure_count_change_vs_baseline=structure_change,
        relative_duration_change_vs_baseline=duration_change,
        relative_state_diversity_change_vs_baseline=diversity_change,
        relative_forward_range_change_vs_baseline=range_change,
        experiment_notes=_comparison_notes(row.status, structure_change, duration_change, diversity_change, range_change),
    )


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _period_from_ohlc(frame: pd.DataFrame) -> tuple[str, str]:
    date_column = _column(frame, "Date")
    if frame.empty or date_column is None:
        return "", ""
    dates = pd.to_datetime(frame[date_column])
    return str(dates.min()), str(dates.max())


def _mean(frame: pd.DataFrame, column: str) -> float:
    actual = _column(frame, column)
    if frame.empty or actual is None:
        return 0.0
    return float(pd.to_numeric(frame[actual], errors="coerce").fillna(0).mean())


def _mode(frame: pd.DataFrame, column: str) -> str:
    actual = _column(frame, column)
    if frame.empty or actual is None:
        return ""
    values = frame[actual].dropna()
    if values.empty:
        return ""
    mode = values.mode()
    return str(mode.iloc[0]) if not mode.empty else ""


def _unique(frame: pd.DataFrame, column: str) -> int:
    actual = _column(frame, column)
    if frame.empty or actual is None:
        return 0
    return int(frame[actual].dropna().nunique())


def _counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    actual = _column(frame, column)
    if frame.empty or actual is None:
        return {state: 0 for state in STATE_TYPES}
    raw = frame[actual].value_counts().to_dict()
    counts = {state: 0 for state in STATE_TYPES}
    counts.update({str(key): int(value) for key, value in raw.items()})
    return counts


def _boolean_rate(frame: pd.DataFrame, column: str) -> float:
    actual = _column(frame, column)
    if frame.empty or actual is None:
        return 0.0
    return float(frame[actual].map(_is_truthy).mean())


def _conditions_evaluated(frame: pd.DataFrame) -> int:
    if frame.empty:
        return 0
    condition_column = _column(frame, "Condition_ID")
    if condition_column is not None:
        return int(frame[condition_column].dropna().nunique())
    return len(frame)


def _low_sample_count(frame: pd.DataFrame) -> int:
    low_sample_column = _column(frame, "Low_Sample_Size")
    if frame.empty or low_sample_column is None:
        return 0
    return int(frame[low_sample_column].map(_is_truthy).sum())


def _most_common_state_count(state_counts: dict[str, int]) -> int:
    return max(state_counts.values()) if state_counts else 0


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def _relative_change(value: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (float(value) - float(baseline)) / float(baseline)


def _column(frame: pd.DataFrame, expected: str) -> str | None:
    lookup = {_normalize_column(column): column for column in frame.columns}
    return lookup.get(_normalize_column(expected))


def _normalize_column(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())


def _is_truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _notes(status: str) -> str:
    if status == "COMPLETED":
        return "Experiment completed; metrics available."
    if status == "SKIPPED":
        return "Existing experiment outputs were used for metric extraction."
    return "Metrics may be incomplete because the experiment run did not complete."


def _comparison_notes(
    status: str,
    structure_change: float,
    duration_change: float,
    diversity_change: float,
    range_change: float,
) -> str:
    if status not in {"COMPLETED", "SKIPPED"}:
        return _notes(status)
    labels = [
        f"structures {_direction_word(structure_change)}",
        f"duration {_direction_word(duration_change)}",
        f"state diversity {_direction_word(diversity_change)}",
        f"forward range {_direction_word(range_change)}",
    ]
    return "Baseline comparison: " + ", ".join(labels) + "."


def _direction_word(value: float) -> str:
    if abs(value) < 0.001:
        return "stable"
    return "increased" if value > 0 else "decreased"
