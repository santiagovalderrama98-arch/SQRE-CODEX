"""Metric extraction for state threshold experiment outputs."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.state_threshold_experiments.models import (
    StateThresholdExperimentMetricsRow,
    StateThresholdExperimentRun,
    StateThresholdExperimentRunResult,
)


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

_ZERO_TOLERANCE = 0.000001


def collect_state_threshold_metrics(
    experiment_run: StateThresholdExperimentRun,
    result: StateThresholdExperimentRunResult,
) -> StateThresholdExperimentMetricsRow:
    ohlc = _read_csv_if_exists(experiment_run.ohlc_path)
    structures = _read_csv_if_exists(experiment_run.processed_dir / "structures.csv")
    states = _read_csv_if_exists(experiment_run.processed_dir / "market_states.csv")
    transitions = _read_csv_if_exists(experiment_run.processed_dir / "state_transitions.csv")
    condition_summaries = _read_csv_if_exists(experiment_run.research_dir / "condition_summaries.csv")
    price_outcomes = _read_csv_if_exists(experiment_run.research_dir / "price_outcomes.csv")
    price_summary = _read_csv_if_exists(experiment_run.research_dir / "condition_price_outcome_summary.csv")

    period_start, period_end = _period_from_ohlc(ohlc)
    state_counts = _counts(states, "Market_State")
    states_generated = len(states)
    conditions_evaluated = _conditions_evaluated(condition_summaries)
    condition_summary_rows = len(condition_summaries)
    low_sample_research = _low_sample_count(condition_summaries)
    price_summary_rows = len(price_summary)
    low_sample_price = _low_sample_count(price_summary)

    return StateThresholdExperimentMetricsRow(
        experiment_run_id=experiment_run.experiment_run_id,
        profile_id=experiment_run.profile_id,
        scenario_id=experiment_run.scenario_id,
        symbol=experiment_run.symbol,
        timeframe=experiment_run.timeframe,
        status=result.status,
        message=result.message,
        period_start=period_start,
        period_end=period_end,
        ohlc_rows=len(ohlc),
        structures_detected=len(structures),
        average_structure_duration=_mean(structures, "Duration_Seconds"),
        average_structural_confidence=_mean(structures, "Structural_Confidence"),
        states_generated=states_generated,
        unique_states=_unique(states, "Market_State"),
        most_common_state=_mode(states, "Market_State"),
        most_common_state_ratio=_safe_ratio(_most_common_state_count(state_counts), states_generated),
        directional_displacement_count=state_counts.get("DIRECTIONAL_DISPLACEMENT", 0),
        directional_expansion_count=state_counts.get("DIRECTIONAL_EXPANSION", 0),
        directional_drift_count=state_counts.get("DIRECTIONAL_DRIFT", 0),
        volatile_rotation_count=state_counts.get("VOLATILE_ROTATION", 0),
        complex_consolidation_count=state_counts.get("COMPLEX_CONSOLIDATION", 0),
        neutral_compression_count=state_counts.get("NEUTRAL_COMPRESSION", 0),
        low_quality_structure_count=state_counts.get("LOW_QUALITY_STRUCTURE", 0),
        unclassified_count=state_counts.get("UNCLASSIFIED", 0),
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
        average_transition_stability=_mean(transitions, "Transition_Stability"),
        conditions_evaluated=conditions_evaluated,
        condition_summary_rows=condition_summary_rows,
        low_sample_conditions_research=low_sample_research,
        research_low_sample_rate=_safe_ratio(low_sample_research, conditions_evaluated),
        price_outcomes_generated=len(price_outcomes),
        price_outcome_summary_rows=price_summary_rows,
        low_sample_conditions_price_outcome=low_sample_price,
        price_outcome_low_sample_rate=_safe_ratio(low_sample_price, price_summary_rows),
        average_forward_range_pips=_mean(price_summary, "Average_Forward_Range_Pips"),
        average_outcome_magnitude_pips=_mean(price_summary, "Average_Outcome_Magnitude_Pips"),
        direction_alignment_rate=_mean(price_summary, "Direction_Alignment_Rate"),
        average_forward_close_return_pips=_mean(price_summary, "Average_Forward_Close_Return_Pips"),
        experiment_notes=_notes(result.status),
    )


def apply_baseline_comparisons(
    rows: Iterable[StateThresholdExperimentMetricsRow],
    baseline_profile_id: str = "state_baseline",
) -> list[StateThresholdExperimentMetricsRow]:
    items = list(rows)
    baselines = {
        row.scenario_id: row
        for row in items
        if row.profile_id == baseline_profile_id and row.status in {"COMPLETED", "SKIPPED"}
    }
    return [_with_comparison(row, baselines.get(row.scenario_id)) for row in items]


def _with_comparison(
    row: StateThresholdExperimentMetricsRow,
    baseline: StateThresholdExperimentMetricsRow | None,
) -> StateThresholdExperimentMetricsRow:
    if baseline is None or row.profile_id == baseline.profile_id:
        return row
    most_common_change = _relative_change(row.most_common_state_ratio, baseline.most_common_state_ratio)
    directional_change = _relative_change(row.directional_state_ratio, baseline.directional_state_ratio)
    diversity_change = _relative_change(row.unique_states, baseline.unique_states)
    rotation_change = _relative_change(row.volatile_rotation_ratio, baseline.volatile_rotation_ratio)
    compression_change = _relative_change(
        row.compression_consolidation_ratio,
        baseline.compression_consolidation_ratio,
    )
    unclassified_change = _relative_change(row.unclassified_rate, baseline.unclassified_rate)
    low_quality_change = _relative_change(row.low_quality_rate, baseline.low_quality_rate)
    range_change = _relative_change(row.average_forward_range_pips, baseline.average_forward_range_pips)
    most_common_delta = _absolute_change(row.most_common_state_ratio, baseline.most_common_state_ratio)
    directional_delta = _absolute_change(row.directional_state_ratio, baseline.directional_state_ratio)
    rotation_delta = _absolute_change(row.volatile_rotation_ratio, baseline.volatile_rotation_ratio)
    compression_delta = _absolute_change(
        row.compression_consolidation_ratio,
        baseline.compression_consolidation_ratio,
    )
    unclassified_delta = _absolute_change(row.unclassified_rate, baseline.unclassified_rate)
    low_quality_delta = _absolute_change(row.low_quality_rate, baseline.low_quality_rate)
    range_delta = _absolute_change(row.average_forward_range_pips, baseline.average_forward_range_pips)
    return replace(
        row,
        relative_most_common_state_ratio_vs_baseline=most_common_change,
        relative_directional_state_ratio_vs_baseline=directional_change,
        relative_state_diversity_change_vs_baseline=diversity_change,
        relative_volatile_rotation_ratio_vs_baseline=rotation_change,
        relative_compression_consolidation_ratio_vs_baseline=compression_change,
        relative_unclassified_rate_vs_baseline=unclassified_change,
        relative_low_quality_rate_vs_baseline=low_quality_change,
        relative_forward_range_change_vs_baseline=range_change,
        absolute_most_common_state_ratio_change_vs_baseline=most_common_delta,
        absolute_directional_state_ratio_change_vs_baseline=directional_delta,
        absolute_volatile_rotation_ratio_change_vs_baseline=rotation_delta,
        absolute_compression_consolidation_ratio_change_vs_baseline=compression_delta,
        absolute_unclassified_rate_change_vs_baseline=unclassified_delta,
        absolute_low_quality_rate_change_vs_baseline=low_quality_delta,
        absolute_forward_range_change_vs_baseline=range_delta,
        experiment_notes=_comparison_notes(row.status, row=row, baseline=baseline),
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


def _absolute_change(value: float, baseline: float) -> float:
    return float(value) - float(baseline)


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
    *,
    row: StateThresholdExperimentMetricsRow,
    baseline: StateThresholdExperimentMetricsRow,
) -> str:
    if status not in {"COMPLETED", "SKIPPED"}:
        return _notes(status)
    labels = [
        f"directional ratio {_change_label(row.directional_state_ratio, baseline.directional_state_ratio)}",
        f"state diversity {_change_label(row.unique_states, baseline.unique_states)}",
        f"unclassified rate {_change_label(row.unclassified_rate, baseline.unclassified_rate)}",
        f"forward range {_change_label(row.average_forward_range_pips, baseline.average_forward_range_pips)}",
    ]
    return "Baseline comparison: " + ", ".join(labels) + "."


def _change_label(value: float, baseline: float) -> str:
    current = float(value)
    reference = float(baseline)
    current_is_zero = abs(current) <= _ZERO_TOLERANCE
    baseline_is_zero = abs(reference) <= _ZERO_TOLERANCE
    if baseline_is_zero and current_is_zero:
        return "stable at zero"
    if baseline_is_zero and current > 0:
        return "increased from zero"
    if reference > 0 and current_is_zero:
        return "decreased to zero"
    return _direction_word(_relative_change(current, reference))


def _direction_word(value: float) -> str:
    if abs(value) < 0.001:
        return "stable"
    return "increased" if value > 0 else "decreased"
