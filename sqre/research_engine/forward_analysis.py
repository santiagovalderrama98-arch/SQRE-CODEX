"""Forward distribution analysis for SQRE Research Engine."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.models import (
    ForwardStateDistributionRow,
    ForwardTransitionDistributionRow,
    ResearchCondition,
    ResearchMarketState,
    ResearchTransition,
)


@dataclass(frozen=True)
class _ForwardStateObservation:
    market_state: str
    confidence: float
    duration_seconds: float


@dataclass(frozen=True)
class _ForwardTransitionObservation:
    transition_label: str
    magnitude: float
    stability: float
    state_confidence_change: float


def analyze_forward_states(
    states: list[ResearchMarketState],
    conditions: list[ResearchCondition],
    config: ResearchEngineConfig,
) -> list[ForwardStateDistributionRow]:
    rows: list[ForwardStateDistributionRow] = []
    state_conditions = [condition for condition in conditions if condition.condition_type == "STATE_CONDITION"]
    grouped_states = _group_states(states)

    for condition in state_conditions:
        for forward_window in config.forward_windows:
            observations, incomplete_cases = _forward_state_observations(
                grouped_states,
                condition.market_state,
                forward_window,
            )
            rows.extend(
                _build_forward_state_rows(
                    condition=condition,
                    forward_window=forward_window,
                    observations=observations,
                    incomplete_cases=incomplete_cases,
                    minimum_sample_size=config.minimum_sample_size,
                )
            )

    return rows


def analyze_forward_transitions(
    transitions: list[ResearchTransition],
    conditions: list[ResearchCondition],
    config: ResearchEngineConfig,
) -> list[ForwardTransitionDistributionRow]:
    rows: list[ForwardTransitionDistributionRow] = []
    transition_conditions = [
        condition
        for condition in conditions
        if condition.condition_type in {"TRANSITION_CONDITION", "TAG_CONDITION"}
    ]
    grouped_transitions = _group_transitions(transitions)

    for condition in transition_conditions:
        observations = _forward_transition_observations(grouped_transitions, condition)
        rows.extend(
            _build_forward_transition_rows(
                condition=condition,
                observations=observations,
                minimum_sample_size=config.minimum_sample_size,
            )
        )

    return rows


def _forward_state_observations(
    grouped_states: dict[tuple[str, str], list[ResearchMarketState]],
    market_state: str,
    forward_window: int,
) -> tuple[list[_ForwardStateObservation], int]:
    observations: list[_ForwardStateObservation] = []
    incomplete_cases = 0

    for group in grouped_states.values():
        for index, state in enumerate(group):
            if state.market_state != market_state:
                continue
            target_index = index + forward_window
            if target_index >= len(group):
                incomplete_cases += 1
                continue
            target = group[target_index]
            observations.append(
                _ForwardStateObservation(
                    market_state=target.market_state,
                    confidence=target.state_confidence,
                    duration_seconds=target.duration_seconds,
                )
            )

    return observations, incomplete_cases


def _forward_transition_observations(
    grouped_transitions: dict[tuple[str, str], list[ResearchTransition]],
    condition: ResearchCondition,
) -> list[_ForwardTransitionObservation]:
    observations: list[_ForwardTransitionObservation] = []

    for group in grouped_transitions.values():
        for index, transition in enumerate(group[:-1]):
            if not _transition_matches_condition(transition, condition):
                continue
            target = group[index + 1]
            observations.append(
                _ForwardTransitionObservation(
                    transition_label=target.transition_label,
                    magnitude=target.transition_magnitude,
                    stability=target.transition_stability,
                    state_confidence_change=target.state_confidence_change,
                )
            )

    return observations


def _build_forward_state_rows(
    *,
    condition: ResearchCondition,
    forward_window: int,
    observations: list[_ForwardStateObservation],
    incomplete_cases: int,
    minimum_sample_size: int,
) -> list[ForwardStateDistributionRow]:
    sample_size = len(observations)
    if sample_size == 0:
        return []

    counts = Counter(observation.market_state for observation in observations)
    rows: list[ForwardStateDistributionRow] = []
    for observed_state, count in sorted(counts.items()):
        matching = [observation for observation in observations if observation.market_state == observed_state]
        frequency = count / sample_size
        rows.append(
            ForwardStateDistributionRow(
                condition_id=condition.condition_id,
                condition_type=condition.condition_type,
                condition_value=condition.condition_value,
                forward_window=forward_window,
                observed_forward_state=observed_state,
                count=count,
                frequency=frequency,
                percentage=frequency * 100,
                sample_size=sample_size,
                incomplete_forward_cases=incomplete_cases,
                average_forward_state_confidence=_average(observation.confidence for observation in matching),
                average_forward_state_duration=_average(
                    observation.duration_seconds for observation in matching
                ),
                low_sample_size=sample_size < minimum_sample_size,
            )
        )
    return rows


def _build_forward_transition_rows(
    *,
    condition: ResearchCondition,
    observations: list[_ForwardTransitionObservation],
    minimum_sample_size: int,
) -> list[ForwardTransitionDistributionRow]:
    sample_size = len(observations)
    if sample_size == 0:
        return []

    counts = Counter(observation.transition_label for observation in observations)
    rows: list[ForwardTransitionDistributionRow] = []
    for transition_label, count in sorted(counts.items()):
        matching = [
            observation for observation in observations if observation.transition_label == transition_label
        ]
        frequency = count / sample_size
        rows.append(
            ForwardTransitionDistributionRow(
                condition_id=condition.condition_id,
                condition_type=condition.condition_type,
                condition_value=condition.condition_value,
                observed_forward_transition=transition_label,
                count=count,
                frequency=frequency,
                percentage=frequency * 100,
                sample_size=sample_size,
                average_forward_transition_magnitude=_average(
                    observation.magnitude for observation in matching
                ),
                average_forward_transition_stability=_average(
                    observation.stability for observation in matching
                ),
                average_forward_state_confidence_change=_average(
                    observation.state_confidence_change for observation in matching
                ),
                low_sample_size=sample_size < minimum_sample_size,
            )
        )
    return rows


def _transition_matches_condition(transition: ResearchTransition, condition: ResearchCondition) -> bool:
    if condition.condition_type == "TRANSITION_CONDITION":
        return transition.transition_label == condition.transition_label
    if condition.condition_type == "TAG_CONDITION":
        return condition.tag in {tag for tag in transition.transition_tags.split("|") if tag}
    return False


def _group_states(states: list[ResearchMarketState]) -> dict[tuple[str, str], list[ResearchMarketState]]:
    groups: dict[tuple[str, str], list[ResearchMarketState]] = defaultdict(list)
    for state in states:
        groups[(state.symbol, state.timeframe)].append(state)
    return {key: sorted(group, key=lambda state: state.start_time) for key, group in groups.items()}


def _group_transitions(
    transitions: list[ResearchTransition],
) -> dict[tuple[str, str], list[ResearchTransition]]:
    groups: dict[tuple[str, str], list[ResearchTransition]] = defaultdict(list)
    for transition in transitions:
        groups[(transition.symbol, transition.timeframe)].append(transition)
    return {
        key: sorted(group, key=lambda transition: transition.start_time)
        for key, group in groups.items()
    }


def _average(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)
