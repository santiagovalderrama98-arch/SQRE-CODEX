"""Research condition generation."""

from __future__ import annotations

from collections import defaultdict

from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.models import ResearchCondition, ResearchMarketState, ResearchTransition


def generate_research_conditions(
    states: list[ResearchMarketState],
    transitions: list[ResearchTransition],
    config: ResearchEngineConfig,
) -> list[ResearchCondition]:
    conditions: list[ResearchCondition] = []
    seen: set[tuple[str, str]] = set()

    for market_state in sorted({state.market_state for state in states}):
        _append_condition(
            conditions,
            seen,
            ResearchCondition(
                condition_id="",
                condition_type="STATE_CONDITION",
                condition_value=market_state,
                market_state=market_state,
            ),
        )

    for transition_label in sorted({transition.transition_label for transition in transitions}):
        from_state, to_state = _split_transition_label(transition_label)
        _append_condition(
            conditions,
            seen,
            ResearchCondition(
                condition_id="",
                condition_type="TRANSITION_CONDITION",
                condition_value=transition_label,
                from_market_state=from_state,
                to_market_state=to_state,
                transition_label=transition_label,
            ),
        )

    for tag in sorted(_unique_tags(transitions)):
        _append_condition(
            conditions,
            seen,
            ResearchCondition(
                condition_id="",
                condition_type="TAG_CONDITION",
                condition_value=tag,
                tag=tag,
            ),
        )

    for sequence in sorted(_observed_sequences(states, config.sequence_length)):
        _append_condition(
            conditions,
            seen,
            ResearchCondition(
                condition_id="",
                condition_type="SEQUENCE_CONDITION",
                condition_value=sequence,
                sequence=sequence,
                sequence_length=config.sequence_length,
            ),
        )

    return [
        ResearchCondition(
            condition_id=f"COND_{index:06d}",
            condition_type=condition.condition_type,
            condition_value=condition.condition_value,
            market_state=condition.market_state,
            from_market_state=condition.from_market_state,
            to_market_state=condition.to_market_state,
            transition_label=condition.transition_label,
            tag=condition.tag,
            sequence=condition.sequence,
            sequence_length=condition.sequence_length,
        )
        for index, condition in enumerate(conditions, start=1)
    ]


def _append_condition(
    conditions: list[ResearchCondition],
    seen: set[tuple[str, str]],
    condition: ResearchCondition,
) -> None:
    key = (condition.condition_type, condition.condition_value)
    if key in seen:
        return
    seen.add(key)
    conditions.append(condition)


def _unique_tags(transitions: list[ResearchTransition]) -> set[str]:
    tags: set[str] = set()
    for transition in transitions:
        tags.update(tag for tag in transition.transition_tags.split("|") if tag)
    return tags


def _observed_sequences(states: list[ResearchMarketState], sequence_length: int) -> set[str]:
    if sequence_length <= 0:
        raise ValueError("sequence_length must be greater than zero")
    sequences: set[str] = set()
    for group in _group_states(states).values():
        ordered = sorted(group, key=lambda state: state.start_time)
        if len(ordered) < sequence_length:
            continue
        for start_index in range(0, len(ordered) - sequence_length + 1):
            window = ordered[start_index : start_index + sequence_length]
            sequences.add(" -> ".join(state.market_state for state in window))
    return sequences


def _group_states(states: list[ResearchMarketState]) -> dict[tuple[str, str], list[ResearchMarketState]]:
    groups: dict[tuple[str, str], list[ResearchMarketState]] = defaultdict(list)
    for state in states:
        groups[(state.symbol, state.timeframe)].append(state)
    return dict(groups)


def _split_transition_label(label: str) -> tuple[str, str]:
    parts = [part.strip() for part in label.split("->", maxsplit=1)]
    if len(parts) != 2:
        return "", ""
    return parts[0], parts[1]
