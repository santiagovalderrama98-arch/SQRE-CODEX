"""Metric extraction for SQRE validation scenarios."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.validation.models import ScenarioMetrics, ScenarioRunResult, ValidationScenario


SUMMARY_COLUMNS = [
    "Scenario_ID",
    "Status",
    "Message",
    "Symbol",
    "Timeframe",
    "OHLC_File",
    "Period_Start",
    "Period_End",
    "OHLC_Rows",
    "Max_Structure_Duration_Seconds",
    "Forward_Windows",
    "Structures_Detected",
    "Average_Structure_Duration",
    "Average_Price_Displacement",
    "Most_Common_Direction",
    "Average_Persistence_Index",
    "Average_Structural_Complexity",
    "Average_Structural_Stability",
    "Average_Structural_Confidence",
    "States_Generated",
    "Unique_States",
    "Most_Common_State",
    "Directional_Displacement_Count",
    "Directional_Expansion_Count",
    "Directional_Drift_Count",
    "Volatile_Rotation_Count",
    "Complex_Consolidation_Count",
    "Neutral_Compression_Count",
    "Low_Quality_Structure_Count",
    "Unclassified_Count",
    "Average_State_Confidence",
    "Transitions_Generated",
    "Unique_Transitions",
    "Most_Common_Transition",
    "Most_Common_Sequence",
    "State_Change_Rate",
    "Direction_Change_Rate",
    "Average_Transition_Magnitude",
    "Average_Transition_Stability",
    "Average_State_Confidence_Change",
    "Average_Structural_Quality_Change",
    "Conditions_Evaluated",
    "Forward_State_Rows",
    "Forward_Transition_Rows",
    "Preceding_State_Rows",
    "Sequence_Outcome_Rows",
    "Condition_Summary_Rows",
    "Low_Sample_Conditions_Research",
    "Price_Outcomes_Generated",
    "Price_Outcome_Summary_Rows",
    "Price_Outcome_Distribution_Rows",
    "Low_Sample_Conditions_Price_Outcome",
    "Average_Forward_Close_Return_Pips",
    "Median_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Favorable_Displacement_Pips",
    "Average_Adverse_Displacement_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
    "Most_Observed_Condition",
    "Largest_Average_Forward_Range_Condition",
    "Highest_Direction_Alignment_Condition",
]

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


def collect_scenario_metrics(scenario: ValidationScenario, result: ScenarioRunResult) -> ScenarioMetrics:
    """Collect scenario metrics from generated CSV files."""

    ohlc = _read_csv_if_exists(scenario.ohlc_path)
    structures = _read_csv_if_exists(scenario.processed_dir / "structures.csv")
    states = _read_csv_if_exists(scenario.processed_dir / "market_states.csv")
    transitions = _read_csv_if_exists(scenario.processed_dir / "state_transitions.csv")
    sequences = _read_csv_if_exists(scenario.processed_dir / "transition_sequences.csv")
    forward_states = _read_csv_if_exists(scenario.research_dir / "forward_state_distributions.csv")
    forward_transitions = _read_csv_if_exists(scenario.research_dir / "forward_transition_distributions.csv")
    preceding_states = _read_csv_if_exists(scenario.research_dir / "preceding_state_distributions.csv")
    sequence_outcomes = _read_csv_if_exists(scenario.research_dir / "sequence_outcomes.csv")
    condition_summaries = _read_csv_if_exists(scenario.research_dir / "condition_summaries.csv")
    price_outcomes = _read_csv_if_exists(scenario.research_dir / "price_outcomes.csv")
    price_summary = _read_csv_if_exists(scenario.research_dir / "condition_price_outcome_summary.csv")
    price_distribution = _read_csv_if_exists(scenario.research_dir / "price_outcome_distributions.csv")

    period_start, period_end = _period_from_ohlc(ohlc)
    state_counts = _counts(states, "Market_State")
    return ScenarioMetrics(
        scenario_id=scenario.scenario_id,
        status=result.status,
        message=result.message,
        symbol=scenario.symbol,
        timeframe=scenario.timeframe,
        ohlc_file=str(scenario.ohlc_path),
        period_start=period_start,
        period_end=period_end,
        ohlc_rows=len(ohlc),
        max_structure_duration_seconds=scenario.max_structure_duration_seconds,
        forward_windows=",".join(str(item) for item in scenario.forward_candles),
        structures_detected=len(structures),
        average_structure_duration=_mean(structures, "Duration_Seconds"),
        average_price_displacement=_mean(structures, "Price_Displacement"),
        most_common_direction=_mode(structures, "Direction"),
        average_persistence_index=_mean(structures, "Persistence_Index"),
        average_structural_complexity=_mean(structures, "Structural_Complexity"),
        average_structural_stability=_mean(structures, "Structural_Stability"),
        average_structural_confidence=_mean(structures, "Structural_Confidence"),
        states_generated=len(states),
        unique_states=_unique(states, "Market_State"),
        most_common_state=_mode(states, "Market_State"),
        directional_displacement_count=state_counts.get("DIRECTIONAL_DISPLACEMENT", 0),
        directional_expansion_count=state_counts.get("DIRECTIONAL_EXPANSION", 0),
        directional_drift_count=state_counts.get("DIRECTIONAL_DRIFT", 0),
        volatile_rotation_count=state_counts.get("VOLATILE_ROTATION", 0),
        complex_consolidation_count=state_counts.get("COMPLEX_CONSOLIDATION", 0),
        neutral_compression_count=state_counts.get("NEUTRAL_COMPRESSION", 0),
        low_quality_structure_count=state_counts.get("LOW_QUALITY_STRUCTURE", 0),
        unclassified_count=state_counts.get("UNCLASSIFIED", 0),
        average_state_confidence=_mean(states, "State_Confidence"),
        transitions_generated=len(transitions),
        unique_transitions=_unique(transitions, "Transition_Label"),
        most_common_transition=_mode(transitions, "Transition_Label"),
        most_common_sequence=_mode(sequences, "Sequence"),
        state_change_rate=_boolean_rate(transitions, "State_Changed"),
        direction_change_rate=_boolean_rate(transitions, "Direction_Changed"),
        average_transition_magnitude=_mean(transitions, "Transition_Magnitude"),
        average_transition_stability=_mean(transitions, "Transition_Stability"),
        average_state_confidence_change=_mean(transitions, "State_Confidence_Change"),
        average_structural_quality_change=_mean(transitions, "Structural_Quality_Change"),
        conditions_evaluated=_conditions_evaluated(condition_summaries),
        forward_state_rows=len(forward_states),
        forward_transition_rows=len(forward_transitions),
        preceding_state_rows=len(preceding_states),
        sequence_outcome_rows=len(sequence_outcomes),
        condition_summary_rows=len(condition_summaries),
        low_sample_conditions_research=_low_sample_count(condition_summaries),
        price_outcomes_generated=len(price_outcomes),
        price_outcome_summary_rows=len(price_summary),
        price_outcome_distribution_rows=len(price_distribution),
        low_sample_conditions_price_outcome=_low_sample_count(price_summary),
        average_forward_close_return_pips=_mean(price_summary, "Average_Forward_Close_Return_Pips"),
        median_forward_close_return_pips=_mean(price_summary, "Median_Forward_Close_Return_Pips"),
        average_forward_range_pips=_mean(price_summary, "Average_Forward_Range_Pips"),
        average_favorable_displacement_pips=_mean(price_summary, "Average_Max_Favorable_Displacement_Pips"),
        average_adverse_displacement_pips=_mean(price_summary, "Average_Max_Adverse_Displacement_Pips"),
        average_outcome_magnitude_pips=_mean(price_summary, "Average_Outcome_Magnitude_Pips"),
        direction_alignment_rate=_mean(price_summary, "Direction_Alignment_Rate"),
        most_observed_condition=_most_observed_condition(price_summary),
        largest_average_forward_range_condition=_max_condition(price_summary, "Average_Forward_Range_Pips"),
        highest_direction_alignment_condition=_max_condition(price_summary, "Direction_Alignment_Rate"),
    )


def metrics_to_frame(metrics: Iterable[ScenarioMetrics]) -> pd.DataFrame:
    rows = []
    for item in metrics:
        raw = asdict(item)
        rows.append({column: raw[_snake(column)] for column in SUMMARY_COLUMNS})
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def write_summary_csv(path: Path | str, metrics: Iterable[ScenarioMetrics]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_to_frame(metrics).to_csv(output_path, index=False)
    return output_path


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
    return int(frame[actual].nunique())


def _counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    actual = _column(frame, column)
    if frame.empty or actual is None:
        return {state: 0 for state in STATE_TYPES}
    counts = frame[actual].value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def _boolean_rate(frame: pd.DataFrame, column: str) -> float:
    actual = _column(frame, column)
    if frame.empty or actual is None:
        return 0.0
    values = frame[actual]
    if values.empty:
        return 0.0
    normalized = values.map(_is_truthy)
    return float(normalized.mean())


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


def _most_observed_condition(frame: pd.DataFrame) -> str:
    condition_column = _column(frame, "Condition_Value")
    sample_column = _column(frame, "Sample_Size")
    if frame.empty or condition_column is None or sample_column is None:
        return ""
    ordered = frame.sort_values([sample_column, condition_column], ascending=[False, True])
    return str(ordered.iloc[0][condition_column]) if not ordered.empty else ""


def _max_condition(frame: pd.DataFrame, column: str) -> str:
    actual = _column(frame, column)
    condition_column = _column(frame, "Condition_Value")
    if frame.empty or actual is None or condition_column is None:
        return ""
    values = frame.copy()
    low_sample_column = _column(values, "Low_Sample_Size")
    if low_sample_column is not None:
        preferred = values[~values[low_sample_column].map(_is_truthy)]
        if not preferred.empty:
            values = preferred
    values[actual] = pd.to_numeric(values[actual], errors="coerce")
    values = values.dropna(subset=[actual])
    if values.empty:
        return ""
    return str(values.sort_values([actual, condition_column], ascending=[False, True]).iloc[0][condition_column])


def _column(frame: pd.DataFrame, expected: str) -> str | None:
    lookup = {_normalize_column(column): column for column in frame.columns}
    return lookup.get(_normalize_column(expected))


def _normalize_column(column: object) -> str:
    return str(column).strip().lower()


def _is_truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _snake(column: str) -> str:
    return column.lower()
