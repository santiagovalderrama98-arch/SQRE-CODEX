"""SQRE Research Engine pipeline."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from sqre.research_engine.conditions import generate_research_conditions
from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.forward_analysis import analyze_forward_states, analyze_forward_transitions
from sqre.research_engine.loader import load_research_states, load_research_transitions
from sqre.research_engine.models import (
    ConditionSummaryRow,
    ForwardStateDistributionRow,
    ForwardTransitionDistributionRow,
    PrecedingStateDistributionRow,
    ResearchEngineSummary,
    ResearchMarketState,
    ResearchTransition,
    SequenceOutcomeRow,
)
from sqre.research_engine.preceding_analysis import analyze_preceding_states
from sqre.research_engine.reports import write_research_engine_report
from sqre.research_engine.sequence_analysis import analyze_sequence_outcomes
from sqre.research_engine.summaries import build_condition_summaries


def run_research_engine(
    states_path: Path | str,
    transitions_path: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: ResearchEngineConfig | None = None,
) -> ResearchEngineSummary:
    active_config = config or ResearchEngineConfig()
    output_directory = Path(output_dir)
    report = Path(report_path)
    output_directory.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)
    conditions = generate_research_conditions(states, transitions, active_config)

    forward_state_rows = analyze_forward_states(states, conditions, active_config)
    forward_transition_rows = analyze_forward_transitions(transitions, conditions, active_config)
    preceding_state_rows = analyze_preceding_states(states, conditions, active_config)
    sequence_outcome_rows = analyze_sequence_outcomes(states, conditions, active_config)
    condition_summary_rows = build_condition_summaries(
        conditions=conditions,
        forward_state_rows=forward_state_rows,
        forward_transition_rows=forward_transition_rows,
        preceding_state_rows=preceding_state_rows,
        sequence_outcome_rows=sequence_outcome_rows,
        config=active_config,
    )

    forward_state_path = output_directory / "forward_state_distributions.csv"
    forward_transition_path = output_directory / "forward_transition_distributions.csv"
    preceding_state_path = output_directory / "preceding_state_distributions.csv"
    sequence_outcomes_path = output_directory / "sequence_outcomes.csv"
    condition_summaries_path = output_directory / "condition_summaries.csv"

    _write_frame(forward_state_path, forward_state_rows, _FORWARD_STATE_COLUMNS)
    _write_frame(forward_transition_path, forward_transition_rows, _FORWARD_TRANSITION_COLUMNS)
    _write_frame(preceding_state_path, preceding_state_rows, _PRECEDING_STATE_COLUMNS)
    _write_frame(sequence_outcomes_path, sequence_outcome_rows, _SEQUENCE_OUTCOME_COLUMNS)
    _write_frame(condition_summaries_path, condition_summary_rows, _CONDITION_SUMMARY_COLUMNS)

    summary = _build_summary(
        states=states,
        transitions=transitions,
        conditions_evaluated=len(conditions),
        config=active_config,
        forward_state_rows=forward_state_rows,
        forward_transition_rows=forward_transition_rows,
        preceding_state_rows=preceding_state_rows,
        sequence_outcome_rows=sequence_outcome_rows,
        condition_summary_rows=condition_summary_rows,
        forward_state_path=forward_state_path,
        forward_transition_path=forward_transition_path,
        preceding_state_path=preceding_state_path,
        sequence_outcomes_path=sequence_outcomes_path,
        condition_summaries_path=condition_summaries_path,
        report_path=report,
    )
    write_research_engine_report(report, summary)
    return summary


_FORWARD_STATE_COLUMNS = [
    "condition_id",
    "condition_type",
    "condition_value",
    "forward_window",
    "observed_forward_state",
    "count",
    "frequency",
    "percentage",
    "sample_size",
    "incomplete_forward_cases",
    "average_forward_state_confidence",
    "average_forward_state_duration",
    "low_sample_size",
]

_FORWARD_TRANSITION_COLUMNS = [
    "condition_id",
    "condition_type",
    "condition_value",
    "observed_forward_transition",
    "count",
    "frequency",
    "percentage",
    "sample_size",
    "average_forward_transition_magnitude",
    "average_forward_transition_stability",
    "average_forward_state_confidence_change",
    "low_sample_size",
]

_PRECEDING_STATE_COLUMNS = [
    "condition_id",
    "condition_type",
    "condition_value",
    "observed_preceding_state",
    "count",
    "frequency",
    "percentage",
    "sample_size",
    "average_preceding_state_confidence",
    "average_preceding_state_duration",
    "low_sample_size",
]

_SEQUENCE_OUTCOME_COLUMNS = [
    "condition_id",
    "condition_type",
    "sequence",
    "sequence_length",
    "observed_forward_state",
    "count",
    "frequency",
    "percentage",
    "sample_size",
    "incomplete_forward_cases",
    "average_forward_state_confidence",
    "low_sample_size",
]

_CONDITION_SUMMARY_COLUMNS = [
    "condition_id",
    "condition_type",
    "condition_value",
    "sample_size",
    "low_sample_size",
    "most_common_forward_state",
    "most_common_forward_state_frequency",
    "forward_state_diversity",
    "most_common_preceding_state",
    "most_common_preceding_state_frequency",
    "average_forward_state_confidence",
    "average_forward_transition_magnitude",
    "average_forward_transition_stability",
    "incomplete_forward_cases",
]


def _write_frame(path: Path, rows: list[object], columns: list[str]) -> None:
    frame = pd.DataFrame([asdict(row) for row in rows], columns=columns)
    frame.to_csv(path, index=False)


def _build_summary(
    *,
    states: list[ResearchMarketState],
    transitions: list[ResearchTransition],
    conditions_evaluated: int,
    config: ResearchEngineConfig,
    forward_state_rows: list[ForwardStateDistributionRow],
    forward_transition_rows: list[ForwardTransitionDistributionRow],
    preceding_state_rows: list[PrecedingStateDistributionRow],
    sequence_outcome_rows: list[SequenceOutcomeRow],
    condition_summary_rows: list[ConditionSummaryRow],
    forward_state_path: Path,
    forward_transition_path: Path,
    preceding_state_path: Path,
    sequence_outcomes_path: Path,
    condition_summaries_path: Path,
    report_path: Path,
) -> ResearchEngineSummary:
    return ResearchEngineSummary(
        symbol=_summary_value([state.symbol for state in states]),
        timeframe=_summary_value([state.timeframe for state in states]),
        period_start=min((state.start_time for state in states), default=None),
        period_end=max((state.end_time for state in states), default=None),
        states_processed=len(states),
        transitions_processed=len(transitions),
        conditions_evaluated=conditions_evaluated,
        forward_windows=list(config.forward_windows),
        minimum_sample_size=config.minimum_sample_size,
        forward_state_rows=len(forward_state_rows),
        forward_transition_rows=len(forward_transition_rows),
        preceding_state_rows=len(preceding_state_rows),
        sequence_outcome_rows=len(sequence_outcome_rows),
        condition_summary_rows=len(condition_summary_rows),
        low_sample_conditions=sum(row.low_sample_size for row in condition_summary_rows),
        most_common_forward_state_result=_most_common(
            row.observed_forward_state for row in forward_state_rows
        ),
        most_common_preceding_state_result=_most_common(
            row.observed_preceding_state for row in preceding_state_rows
        ),
        most_common_sequence_outcome=_most_common(
            row.observed_forward_state for row in sequence_outcome_rows
        ),
        forward_state_distributions_path=forward_state_path,
        forward_transition_distributions_path=forward_transition_path,
        preceding_state_distributions_path=preceding_state_path,
        sequence_outcomes_path=sequence_outcomes_path,
        condition_summaries_path=condition_summaries_path,
        report_path=report_path,
    )


def _summary_value(values: list[str]) -> str:
    unique_values = sorted(set(values))
    if not unique_values:
        return "UNKNOWN"
    if len(unique_values) == 1:
        return unique_values[0]
    return "MULTIPLE"


def _most_common(values: object) -> str:
    counts = Counter(values)
    if not counts:
        return "NONE"
    return counts.most_common(1)[0][0]
