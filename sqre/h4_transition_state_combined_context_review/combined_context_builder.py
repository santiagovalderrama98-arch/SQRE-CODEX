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
    source = _find_state(transition.source_state, transition.forward_window, states)
    target = _find_state(transition.target_state, transition.forward_window, states)
    if source is not None and target is not None:
        return _combine_state_contexts(source, target)
    if source is not None:
        return source
    if target is not None:
        return target
    return summary


def _find_state(
    state_label: str,
    forward_window: str,
    states: dict[tuple[str, str], StateContext],
) -> StateContext | None:
    for key in [(state_label, forward_window), (state_label, "")]:
        state = states.get(key)
        if state is not None:
            return state
    return None


def _combine_state_contexts(source: StateContext, target: StateContext) -> StateContext:
    dominant = source if _rank(source.dispersion_status) >= _rank(target.dispersion_status) else target
    sensitivity = source.sensitivity_status
    if sensitivity.endswith("UNAVAILABLE") and not target.sensitivity_status.endswith("UNAVAILABLE"):
        sensitivity = target.sensitivity_status
    readiness = source.readiness_flag
    if readiness.endswith("UNAVAILABLE") and not target.readiness_flag.endswith("UNAVAILABLE"):
        readiness = target.readiness_flag
    return StateContext(
        state_label=f"{source.state_label} | {target.state_label}",
        forward_window=source.forward_window or target.forward_window,
        profile_status=dominant.profile_status,
        dispersion_status=dominant.dispersion_status,
        sensitivity_status=sensitivity,
        readiness_flag=readiness,
        sample_size=source.sample_size + target.sample_size,
    )


def _rank(value: str) -> int:
    text = str(value or "").upper()
    if "HIGH" in text or "SCENARIO_SENSITIVE" in text:
        return 5
    if "MODERATE" in text:
        return 4
    if "STABLE" in text or "DESCRIPTIVE" in text or "CONSISTENT" in text:
        return 3
    if "SAMPLE" in text or "CONSTRAINED" in text:
        return 2
    if not text or "UNAVAILABLE" in text or "MISSING" in text:
        return 0
    return 1


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
