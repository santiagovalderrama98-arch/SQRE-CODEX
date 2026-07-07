"""Condition summaries for SQRE Research Engine."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, TypeVar

from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.models import (
    ConditionSummaryRow,
    ForwardStateDistributionRow,
    ForwardTransitionDistributionRow,
    PrecedingStateDistributionRow,
    ResearchCondition,
    SequenceOutcomeRow,
)

RowT = TypeVar("RowT")


def build_condition_summaries(
    conditions: list[ResearchCondition],
    forward_state_rows: list[ForwardStateDistributionRow],
    forward_transition_rows: list[ForwardTransitionDistributionRow],
    preceding_state_rows: list[PrecedingStateDistributionRow],
    sequence_outcome_rows: list[SequenceOutcomeRow],
    config: ResearchEngineConfig,
) -> list[ConditionSummaryRow]:
    state_rows_by_condition = _group_by_condition(forward_state_rows)
    transition_rows_by_condition = _group_by_condition(forward_transition_rows)
    preceding_rows_by_condition = _group_by_condition(preceding_state_rows)
    sequence_rows_by_condition = _group_by_condition(sequence_outcome_rows)

    summaries: list[ConditionSummaryRow] = []
    for condition in conditions:
        forward_state_matches = _summary_forward_state_rows(
            condition,
            state_rows_by_condition.get(condition.condition_id, []),
            sequence_rows_by_condition.get(condition.condition_id, []),
        )
        transition_matches = transition_rows_by_condition.get(condition.condition_id, [])
        preceding_matches = preceding_rows_by_condition.get(condition.condition_id, [])

        sample_size = _condition_sample_size(condition, forward_state_matches, transition_matches)
        summaries.append(
            ConditionSummaryRow(
                condition_id=condition.condition_id,
                condition_type=condition.condition_type,
                condition_value=condition.condition_value,
                sample_size=sample_size,
                low_sample_size=sample_size < config.minimum_sample_size,
                most_common_forward_state=_most_common_value(
                    forward_state_matches,
                    value_attr="observed_forward_state",
                ),
                most_common_forward_state_frequency=_most_common_frequency(forward_state_matches),
                forward_state_diversity=len(
                    {getattr(row, "observed_forward_state") for row in forward_state_matches}
                ),
                most_common_preceding_state=_most_common_value(
                    preceding_matches,
                    value_attr="observed_preceding_state",
                ),
                most_common_preceding_state_frequency=_most_common_frequency(preceding_matches),
                average_forward_state_confidence=_weighted_average(
                    forward_state_matches,
                    value_attr="average_forward_state_confidence",
                ),
                average_forward_transition_magnitude=_weighted_average(
                    transition_matches,
                    value_attr="average_forward_transition_magnitude",
                ),
                average_forward_transition_stability=_weighted_average(
                    transition_matches,
                    value_attr="average_forward_transition_stability",
                ),
                incomplete_forward_cases=sum(
                    getattr(row, "incomplete_forward_cases", 0) for row in forward_state_matches
                ),
            )
        )

    return summaries


def _summary_forward_state_rows(
    condition: ResearchCondition,
    forward_state_rows: list[ForwardStateDistributionRow],
    sequence_rows: list[SequenceOutcomeRow],
) -> list[ForwardStateDistributionRow | SequenceOutcomeRow]:
    if condition.condition_type == "STATE_CONDITION":
        return [row for row in forward_state_rows if row.forward_window == 1]
    if condition.condition_type == "SEQUENCE_CONDITION":
        return sequence_rows
    return []


def _condition_sample_size(
    condition: ResearchCondition,
    forward_state_rows: list[ForwardStateDistributionRow | SequenceOutcomeRow],
    transition_rows: list[ForwardTransitionDistributionRow],
) -> int:
    if condition.condition_type in {"STATE_CONDITION", "SEQUENCE_CONDITION"}:
        return _max_sample_size(forward_state_rows)
    if condition.condition_type in {"TRANSITION_CONDITION", "TAG_CONDITION"}:
        return _max_sample_size(transition_rows)
    return 0


def _group_by_condition(rows: Iterable[RowT]) -> dict[str, list[RowT]]:
    grouped: dict[str, list[RowT]] = defaultdict(list)
    for row in rows:
        grouped[getattr(row, "condition_id")].append(row)
    return dict(grouped)


def _max_sample_size(rows: Iterable[object]) -> int:
    return max((int(getattr(row, "sample_size")) for row in rows), default=0)


def _most_common_value(rows: list[object], *, value_attr: str) -> str:
    if not rows:
        return "NONE"
    best = max(rows, key=lambda row: (getattr(row, "count"), getattr(row, "frequency"), getattr(row, value_attr)))
    return str(getattr(best, value_attr))


def _most_common_frequency(rows: list[object]) -> float:
    if not rows:
        return 0.0
    best = max(rows, key=lambda row: (getattr(row, "count"), getattr(row, "frequency")))
    return float(getattr(best, "frequency"))


def _weighted_average(rows: list[object], *, value_attr: str) -> float:
    total_count = sum(int(getattr(row, "count")) for row in rows)
    if total_count == 0:
        return 0.0
    return sum(float(getattr(row, value_attr)) * int(getattr(row, "count")) for row in rows) / total_count
