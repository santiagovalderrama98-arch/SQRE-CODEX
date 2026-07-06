"""Transition sequence analysis."""

from __future__ import annotations

from collections import defaultdict

from sqre.transition_engine.config import TransitionEngineConfig
from sqre.transition_engine.models import MarketStateInput, StateTransition, TransitionSequence


def build_transition_sequences(
    states: list[MarketStateInput],
    transitions: list[StateTransition],
    config: TransitionEngineConfig,
) -> list[TransitionSequence]:
    if config.sequence_length <= 0:
        raise ValueError("sequence_length must be greater than zero")

    occurrences: dict[str, list[tuple[float, float]]] = defaultdict(list)
    transition_lookup = {
        (transition.from_state_id, transition.to_state_id): transition for transition in transitions
    }

    for group in _group_states(states).values():
        ordered_states = sorted(group, key=lambda state: state.start_time)
        if len(ordered_states) < config.sequence_length:
            continue
        for start_index in range(0, len(ordered_states) - config.sequence_length + 1):
            window = ordered_states[start_index : start_index + config.sequence_length]
            sequence = " -> ".join(state.market_state for state in window)
            duration = (window[-1].end_time - window[0].start_time).total_seconds()
            magnitude = _window_average_magnitude(window, transition_lookup)
            occurrences[sequence].append((duration, magnitude))

    total_occurrences = sum(len(values) for values in occurrences.values())
    sequences: list[TransitionSequence] = []
    for index, (sequence, values) in enumerate(_ordered_occurrences(occurrences), start=1):
        count = len(values)
        frequency = count / total_occurrences if total_occurrences else 0.0
        sequences.append(
            TransitionSequence(
                sequence_id=f"SEQ_{index:06d}",
                sequence=sequence,
                length=config.sequence_length,
                count=count,
                frequency=frequency,
                percentage=frequency * 100,
                average_duration=sum(value[0] for value in values) / count,
                average_transition_magnitude=sum(value[1] for value in values) / count,
            )
        )
    return sequences


def _group_states(states: list[MarketStateInput]) -> dict[tuple[str, str], list[MarketStateInput]]:
    groups: dict[tuple[str, str], list[MarketStateInput]] = defaultdict(list)
    for state in states:
        groups[(state.symbol, state.timeframe)].append(state)
    return dict(groups)


def _window_average_magnitude(
    window: list[MarketStateInput],
    transition_lookup: dict[tuple[str, str], StateTransition],
) -> float:
    magnitudes: list[float] = []
    for from_state, to_state in zip(window, window[1:]):
        transition = transition_lookup.get((from_state.state_id, to_state.state_id))
        if transition is not None:
            magnitudes.append(transition.metrics.transition_magnitude)
    if not magnitudes:
        return 0.0
    return sum(magnitudes) / len(magnitudes)


def _ordered_occurrences(
    occurrences: dict[str, list[tuple[float, float]]]
) -> list[tuple[str, list[tuple[float, float]]]]:
    return sorted(occurrences.items(), key=lambda item: (-len(item[1]), item[0]))
