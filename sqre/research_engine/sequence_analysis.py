"""Sequence outcome analysis for SQRE Research Engine."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.models import ResearchCondition, ResearchMarketState, SequenceOutcomeRow


@dataclass(frozen=True)
class _SequenceOutcomeObservation:
    market_state: str
    confidence: float


def analyze_sequence_outcomes(
    states: list[ResearchMarketState],
    conditions: list[ResearchCondition],
    config: ResearchEngineConfig,
) -> list[SequenceOutcomeRow]:
    rows: list[SequenceOutcomeRow] = []
    sequence_conditions = [
        condition for condition in conditions if condition.condition_type == "SEQUENCE_CONDITION"
    ]
    grouped_states = _group_states(states)

    for condition in sequence_conditions:
        observations, incomplete_cases = _sequence_observations(grouped_states, condition.sequence)
        rows.extend(
            _build_rows(
                condition=condition,
                observations=observations,
                incomplete_cases=incomplete_cases,
                minimum_sample_size=config.minimum_sample_size,
            )
        )

    return rows


def _sequence_observations(
    grouped_states: dict[tuple[str, str], list[ResearchMarketState]],
    sequence: str,
) -> tuple[list[_SequenceOutcomeObservation], int]:
    observed_sequence = [item.strip() for item in sequence.split("->")]
    sequence_length = len(observed_sequence)
    observations: list[_SequenceOutcomeObservation] = []
    incomplete_cases = 0

    for group in grouped_states.values():
        if len(group) < sequence_length:
            continue
        for start_index in range(0, len(group) - sequence_length + 1):
            window = group[start_index : start_index + sequence_length]
            if [state.market_state for state in window] != observed_sequence:
                continue
            target_index = start_index + sequence_length
            if target_index >= len(group):
                incomplete_cases += 1
                continue
            target = group[target_index]
            observations.append(
                _SequenceOutcomeObservation(
                    market_state=target.market_state,
                    confidence=target.state_confidence,
                )
            )

    return observations, incomplete_cases


def _build_rows(
    *,
    condition: ResearchCondition,
    observations: list[_SequenceOutcomeObservation],
    incomplete_cases: int,
    minimum_sample_size: int,
) -> list[SequenceOutcomeRow]:
    sample_size = len(observations)
    if sample_size == 0:
        return []

    counts = Counter(observation.market_state for observation in observations)
    rows: list[SequenceOutcomeRow] = []
    for forward_state, count in sorted(counts.items()):
        matching = [observation for observation in observations if observation.market_state == forward_state]
        frequency = count / sample_size
        rows.append(
            SequenceOutcomeRow(
                condition_id=condition.condition_id,
                condition_type=condition.condition_type,
                sequence=condition.sequence,
                sequence_length=condition.sequence_length,
                observed_forward_state=forward_state,
                count=count,
                frequency=frequency,
                percentage=frequency * 100,
                sample_size=sample_size,
                incomplete_forward_cases=incomplete_cases,
                average_forward_state_confidence=_average(observation.confidence for observation in matching),
                low_sample_size=sample_size < minimum_sample_size,
            )
        )
    return rows


def _group_states(states: list[ResearchMarketState]) -> dict[tuple[str, str], list[ResearchMarketState]]:
    groups: dict[tuple[str, str], list[ResearchMarketState]] = defaultdict(list)
    for state in states:
        groups[(state.symbol, state.timeframe)].append(state)
    return {key: sorted(group, key=lambda state: state.start_time) for key, group in groups.items()}


def _average(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)
