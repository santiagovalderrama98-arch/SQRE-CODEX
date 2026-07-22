"""Build combined state/transition context inventory rows."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.models import (
    CombinedContextInventoryRow,
    PartialContext,
    StateContext,
    TransitionContext,
)


def build_combined_context_inventory(
    transitions: list[TransitionContext],
    states: dict[tuple[str, str], StateContext],
    state_summary: StateContext,
    partial: PartialContext,
    config: H4TransitionStateCombinedContextReviewConfig,
) -> list[CombinedContextInventoryRow]:
    rows: list[CombinedContextInventoryRow] = []
    for index, transition in enumerate(transitions, start=1):
        state = _match_state_context(transition, states, state_summary)
        rows.append(
            CombinedContextInventoryRow(
                context_id=f"CTX_{index:06d}",
                symbol=config.symbol,
                timeframe=config.timeframe,
                source_state=transition.source_state,
                target_state=transition.target_state,
                transition_label=transition.transition_label,
                forward_window=transition.forward_window,
                state_profile_status=state.profile_status,
                transition_profile_status=transition.profile_status,
                state_dispersion_status=state.dispersion_status,
                transition_dispersion_status=transition.dispersion_status,
                state_sensitivity_status=state.sensitivity_status,
                transition_sensitivity_status=transition.sensitivity_status,
                partial_context_status=_partial_context_status(partial),
                context_inventory_diagnostic=_diagnostic(state, transition, partial),
            )
        )
    return rows


def _match_state_context(
    transition: TransitionContext,
    states: dict[tuple[str, str], StateContext],
    summary: StateContext,
) -> StateContext:
    candidates = [
        (transition.source_state, transition.forward_window),
        (transition.target_state, transition.forward_window),
        (transition.source_state, ""),
        (transition.target_state, ""),
    ]
    for key in candidates:
        state = states.get(key)
        if state is not None:
            return state
    return summary


def _partial_context_status(partial: PartialContext) -> str:
    if partial.partial_interpretation_class == "PARTIAL_CONTEXT_UNAVAILABLE":
        return "PARTIAL_CONTEXT_UNAVAILABLE"
    return "PARTIAL_CONTEXT_AVAILABLE"


def _diagnostic(state: StateContext, transition: TransitionContext, partial: PartialContext) -> str:
    notes = []
    if state.profile_status.endswith("UNAVAILABLE"):
        notes.append("State baseline context is limited.")
    if transition.profile_status.endswith("UNAVAILABLE"):
        notes.append("Transition baseline context is limited.")
    if partial.partial_interpretation_class == "PARTIAL_CONTEXT_UNAVAILABLE":
        notes.append("Partial context is unavailable.")
    if not notes:
        return "Combined context row assembled from available descriptive inputs."
    return " ".join(notes)
