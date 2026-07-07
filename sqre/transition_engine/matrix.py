"""Transition matrix construction."""

from __future__ import annotations

from collections import Counter, defaultdict

from sqre.transition_engine.models import StateTransition, TransitionMatrixRow


def build_transition_matrix(transitions: list[StateTransition]) -> list[TransitionMatrixRow]:
    grouped: dict[tuple[str, str], list[StateTransition]] = defaultdict(list)
    from_counts = Counter(transition.from_market_state for transition in transitions)

    for transition in transitions:
        grouped[(transition.from_market_state, transition.to_market_state)].append(transition)

    rows: list[TransitionMatrixRow] = []
    for (from_state, to_state), group in sorted(grouped.items()):
        count = len(group)
        probability = count / from_counts[from_state] if from_counts[from_state] else 0.0
        rows.append(
            TransitionMatrixRow(
                from_state=from_state,
                to_state=to_state,
                count=count,
                probability=probability,
                percentage=probability * 100,
                average_transition_magnitude=_average(
                    transition.metrics.transition_magnitude for transition in group
                ),
                average_transition_stability=_average(
                    transition.metrics.transition_stability for transition in group
                ),
                average_state_confidence_change=_average(
                    transition.metrics.state_confidence_change for transition in group
                ),
                average_structural_quality_change=_average(
                    transition.metrics.structural_quality_change for transition in group
                ),
            )
        )
    return rows


def _average(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
