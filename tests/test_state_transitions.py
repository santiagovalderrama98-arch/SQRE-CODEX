from __future__ import annotations

from datetime import datetime, timedelta

from sqre.transition_engine.config import TransitionEngineConfig
from sqre.transition_engine.models import MarketStateInput
from sqre.transition_engine.transitions import build_state_transitions


def state(
    index: int,
    *,
    symbol: str = "EURUSD",
    timeframe: str = "M5",
    market_state: str = "DIRECTIONAL_EXPANSION",
    direction: str = "UP",
    start_offset: int | None = None,
) -> MarketStateInput:
    offset = index if start_offset is None else start_offset
    start = datetime(2026, 1, 1) + timedelta(minutes=offset * 5)
    return MarketStateInput(
        state_id=f"STATE_{index:06d}",
        structure_id=f"STR_{index:06d}",
        symbol=symbol,
        timeframe=timeframe,
        start_time=start,
        end_time=start + timedelta(minutes=5),
        direction=direction,
        market_state=market_state,
        state_confidence=0.7,
        classification_rule="test_rule",
        persistence_index=0.5,
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


def test_build_state_transitions_generates_n_minus_one_per_group() -> None:
    states = [
        state(1, symbol="EURUSD"),
        state(2, symbol="EURUSD", market_state="DIRECTIONAL_DRIFT"),
        state(3, symbol="GBPUSD"),
        state(4, symbol="GBPUSD", market_state="NEUTRAL_COMPRESSION"),
        state(5, symbol="GBPUSD", market_state="VOLATILE_ROTATION"),
    ]

    transitions = build_state_transitions(states, TransitionEngineConfig())

    assert len(transitions) == 3
    assert [transition.transition_id for transition in transitions] == [
        "TRN_000001",
        "TRN_000002",
        "TRN_000003",
    ]
    assert all(transition.from_state_id != "STATE_000002" or transition.to_state_id != "STATE_000003" for transition in transitions)


def test_build_state_transitions_does_not_cross_timeframes() -> None:
    states = [
        state(1, timeframe="M5"),
        state(2, timeframe="H1"),
        state(3, timeframe="M5"),
    ]

    transitions = build_state_transitions(states, TransitionEngineConfig())

    assert len(transitions) == 1
    assert transitions[0].from_state_id == "STATE_000001"
    assert transitions[0].to_state_id == "STATE_000003"


def test_build_state_transitions_sets_flags_label_type_and_tags() -> None:
    states = [
        state(1, market_state="DIRECTIONAL_EXPANSION", direction="UP"),
        state(2, market_state="DIRECTIONAL_DRIFT", direction="DOWN"),
    ]

    transition = build_state_transitions(states, TransitionEngineConfig())[0]

    assert transition.state_changed is True
    assert transition.direction_changed is True
    assert transition.primary_transition_type == "DIRECTION_CHANGE"
    assert transition.transition_label == "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DRIFT"
    assert transition.transition_tags.count("|") == 2


def test_build_state_transitions_primary_type_same_state_and_state_change() -> None:
    same_state = build_state_transitions(
        [state(1, market_state="A", direction="UP"), state(2, market_state="A", direction="UP")],
        TransitionEngineConfig(),
    )[0]
    state_change = build_state_transitions(
        [state(1, market_state="A", direction="UP"), state(2, market_state="B", direction="UP")],
        TransitionEngineConfig(),
    )[0]

    assert same_state.primary_transition_type == "SAME_STATE"
    assert state_change.primary_transition_type == "STATE_CHANGE"
