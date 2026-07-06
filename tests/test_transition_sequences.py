from __future__ import annotations

from datetime import datetime, timedelta

from sqre.transition_engine.config import TransitionEngineConfig
from sqre.transition_engine.models import MarketStateInput
from sqre.transition_engine.sequences import build_transition_sequences
from sqre.transition_engine.transitions import build_state_transitions


def state(index: int, market_state: str, *, symbol: str = "EURUSD") -> MarketStateInput:
    start = datetime(2026, 1, 1) + timedelta(minutes=index * 5)
    return MarketStateInput(
        state_id=f"STATE_{index:06d}",
        structure_id=f"STR_{index:06d}",
        symbol=symbol,
        timeframe="M5",
        start_time=start,
        end_time=start + timedelta(minutes=5),
        direction="UP",
        market_state=market_state,
        state_confidence=0.7 + index * 0.01,
        classification_rule="rule",
        persistence_index=0.3 + index * 0.01,
        structural_complexity=0.4,
        structural_stability=0.7,
        structural_efficiency=0.6,
        event_density=0.4,
        structural_volatility=0.3,
        structural_symmetry=0.8,
        structural_confidence=0.75,
        duration_seconds=300,
        price_displacement=0.001,
        event_count=5,
        leg_count=2,
    )


def test_transition_sequences_use_sliding_windows_and_count_repeated_sequences() -> None:
    config = TransitionEngineConfig(sequence_length=3)
    states = [
        state(1, "A"),
        state(2, "B"),
        state(3, "C"),
        state(4, "A"),
        state(5, "B"),
        state(6, "C"),
    ]
    transitions = build_state_transitions(states, config)

    sequences = build_transition_sequences(states, transitions, config)

    abc = next(sequence for sequence in sequences if sequence.sequence == "A -> B -> C")
    assert abc.sequence_id == "SEQ_000001"
    assert abc.length == 3
    assert abc.count == 2
    assert round(abc.frequency, 4) == round(2 / 4, 4)
    assert round(abc.percentage, 4) == 50.0
    assert abc.average_duration == 15 * 60
    assert abc.average_transition_magnitude > 0


def test_transition_sequences_are_empty_when_not_enough_states() -> None:
    config = TransitionEngineConfig(sequence_length=4)
    states = [state(1, "A"), state(2, "B"), state(3, "C")]
    transitions = build_state_transitions(states, config)

    assert build_transition_sequences(states, transitions, config) == []
