"""Preceding state analysis for SQRE Research Engine."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.models import (
    PrecedingStateDistributionRow,
    ResearchCondition,
    ResearchMarketState,
)


@dataclass(frozen=True)
class _PrecedingStateObservation:
    market_state: str
    confidence: float
    duration_seconds: float


def analyze_preceding_states(
    states: list[ResearchMarketState],
    conditions: list[ResearchCondition],
    config: ResearchEngineConfig,
) -> list[PrecedingStateDistributionRow]:
    rows: list[PrecedingStateDistributionRow] = []
    state_conditions = [condition for condition in conditions if condition.condition_type == "STATE_CONDITION"]
    grouped_states = _group_states(states)

    for condition in state_conditions:
        observations = _preceding_state_observations(grouped_states, condition.market_state)
        rows.extend(
            _build_rows(
                condition=condition,
                observations=observations,
                minimum_sample_size=config.minimum_sample_size,
            )
        )

    return rows


def _preceding_state_observations(
    grouped_states: dict[tuple[str, str], list[ResearchMarketState]],
    market_state: str,
) -> list[_PrecedingStateObservation]:
    observations: list[_PrecedingStateObservation] = []
    for group in grouped_states.values():
        for index, state in enumerate(group):
            if index == 0 or state.market_state != market_state:
                continue
            preceding = group[index - 1]
            observations.append(
                _PrecedingStateObservation(
                    market_state=preceding.market_state,
                    confidence=preceding.state_confidence,
                    duration_seconds=preceding.duration_seconds,
                )
            )
    return observations


def _build_rows(
    *,
    condition: ResearchCondition,
    observations: list[_PrecedingStateObservation],
    minimum_sample_size: int,
) -> list[PrecedingStateDistributionRow]:
    sample_size = len(observations)
    if sample_size == 0:
        return []

    counts = Counter(observation.market_state for observation in observations)
    rows: list[PrecedingStateDistributionRow] = []
    for preceding_state, count in sorted(counts.items()):
        matching = [observation for observation in observations if observation.market_state == preceding_state]
        frequency = count / sample_size
        rows.append(
            PrecedingStateDistributionRow(
                condition_id=condition.condition_id,
                condition_type=condition.condition_type,
                condition_value=condition.condition_value,
                observed_preceding_state=preceding_state,
                count=count,
                frequency=frequency,
                percentage=frequency * 100,
                sample_size=sample_size,
                average_preceding_state_confidence=_average(observation.confidence for observation in matching),
                average_preceding_state_duration=_average(
                    observation.duration_seconds for observation in matching
                ),
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
