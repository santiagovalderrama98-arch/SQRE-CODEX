"""State transition construction."""

from __future__ import annotations

from collections import defaultdict

from sqre.transition_engine.config import TransitionEngineConfig
from sqre.transition_engine.metrics import (
    calculate_transition_metrics,
    classify_confidence_transition,
    classify_magnitude,
    classify_structural_transition,
)
from sqre.transition_engine.models import MarketStateInput, StateTransition


def build_state_transitions(
    states: list[MarketStateInput],
    config: TransitionEngineConfig,
) -> list[StateTransition]:
    transitions: list[StateTransition] = []
    transition_index = 1

    for group in _group_states(states).values():
        ordered_states = sorted(group, key=lambda state: state.start_time)
        for from_state, to_state in zip(ordered_states, ordered_states[1:]):
            transitions.append(_build_transition(transition_index, from_state, to_state, config))
            transition_index += 1

    return transitions


def _group_states(states: list[MarketStateInput]) -> dict[tuple[str, str], list[MarketStateInput]]:
    groups: dict[tuple[str, str], list[MarketStateInput]] = defaultdict(list)
    for state in states:
        groups[(state.symbol, state.timeframe)].append(state)
    return dict(groups)


def _build_transition(
    index: int,
    from_state: MarketStateInput,
    to_state: MarketStateInput,
    config: TransitionEngineConfig,
) -> StateTransition:
    metrics = calculate_transition_metrics(from_state, to_state, config)
    state_changed = from_state.market_state != to_state.market_state
    direction_changed = from_state.direction != to_state.direction
    primary_transition_type = _primary_transition_type(state_changed, direction_changed)
    transition_tags = "|".join(
        [
            classify_confidence_transition(metrics.state_confidence_change, config),
            classify_structural_transition(metrics.structural_quality_change, config),
            classify_magnitude(metrics.transition_magnitude, config),
        ]
    )
    transition_duration = (to_state.start_time - from_state.end_time).total_seconds()

    return StateTransition(
        transition_id=f"TRN_{index:06d}",
        from_state_id=from_state.state_id,
        to_state_id=to_state.state_id,
        from_structure_id=from_state.structure_id,
        to_structure_id=to_state.structure_id,
        symbol=from_state.symbol,
        timeframe=from_state.timeframe,
        from_market_state=from_state.market_state,
        to_market_state=to_state.market_state,
        transition_label=f"{from_state.market_state} -> {to_state.market_state}",
        start_time=from_state.end_time,
        end_time=to_state.start_time,
        transition_duration_seconds=transition_duration,
        from_direction=from_state.direction,
        to_direction=to_state.direction,
        state_changed=state_changed,
        direction_changed=direction_changed,
        primary_transition_type=primary_transition_type,
        transition_tags=transition_tags,
        metrics=metrics,
    )


def _primary_transition_type(state_changed: bool, direction_changed: bool) -> str:
    if direction_changed:
        return "DIRECTION_CHANGE"
    if state_changed:
        return "STATE_CHANGE"
    return "SAME_STATE"
