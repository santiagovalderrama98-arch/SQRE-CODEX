"""Research condition generation for price outcomes."""

from __future__ import annotations

from sqre.price_outcome_research.models import (
    PriceOutcomeCondition,
    PriceOutcomeState,
    PriceOutcomeTransition,
)


def generate_price_outcome_conditions(
    states: list[PriceOutcomeState],
    transitions: list[PriceOutcomeTransition],
) -> list[PriceOutcomeCondition]:
    conditions: list[PriceOutcomeCondition] = []
    seen: set[tuple[str, str]] = set()

    for market_state in sorted({state.market_state for state in states}):
        _append_condition(
            conditions,
            seen,
            PriceOutcomeCondition(
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
            PriceOutcomeCondition(
                condition_id="",
                condition_type="TRANSITION_CONDITION",
                condition_value=transition_label,
                transition_label=transition_label,
                from_market_state=from_state,
                to_market_state=to_state,
            ),
        )

    return [
        PriceOutcomeCondition(
            condition_id=f"COND_{index:06d}",
            condition_type=condition.condition_type,
            condition_value=condition.condition_value,
            market_state=condition.market_state,
            transition_label=condition.transition_label,
            from_market_state=condition.from_market_state,
            to_market_state=condition.to_market_state,
        )
        for index, condition in enumerate(conditions, start=1)
    ]


def _append_condition(
    conditions: list[PriceOutcomeCondition],
    seen: set[tuple[str, str]],
    condition: PriceOutcomeCondition,
) -> None:
    key = (condition.condition_type, condition.condition_value)
    if key in seen:
        return
    seen.add(key)
    conditions.append(condition)


def _split_transition_label(label: str) -> tuple[str, str]:
    parts = [part.strip() for part in label.split("->", maxsplit=1)]
    if len(parts) != 2:
        return "", ""
    return parts[0], parts[1]
