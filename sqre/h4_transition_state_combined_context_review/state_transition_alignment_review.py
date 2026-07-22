"""State/transition alignment review."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.classification import (
    is_high,
    is_sample_constrained,
    is_unavailable,
)
from sqre.h4_transition_state_combined_context_review.models import (
    AlignmentReviewRow,
    CombinedContextInventoryRow,
)


def build_alignment_review(rows: list[CombinedContextInventoryRow]) -> list[AlignmentReviewRow]:
    return [_build_row(row) for row in rows]


def _build_row(row: CombinedContextInventoryRow) -> AlignmentReviewRow:
    state_ready = row.state_sensitivity_status
    transition_ready = row.transition_sensitivity_status
    state_dispersion = row.state_dispersion_status
    transition_dispersion = row.transition_dispersion_status
    alignment = _alignment_class(state_ready, transition_ready, state_dispersion, transition_dispersion)
    return AlignmentReviewRow(
        context_id=row.context_id,
        source_state=row.source_state,
        target_state=row.target_state,
        transition_label=row.transition_label,
        forward_window=row.forward_window,
        state_readiness_flag=state_ready,
        transition_readiness_flag=transition_ready,
        state_dispersion_class=state_dispersion,
        transition_dispersion_class=transition_dispersion,
        state_transition_alignment_class=alignment,
        state_transition_alignment_diagnostic=_diagnostic(alignment),
    )


def _alignment_class(state_status: str, transition_status: str, state_dispersion: str, transition_dispersion: str) -> str:
    if is_high(state_status) and is_high(transition_status):
        return "STATE_TRANSITION_ALIGNED_SCENARIO_SENSITIVE"
    if is_sample_constrained(state_status) or is_sample_constrained(transition_status):
        return "STATE_TRANSITION_ALIGNED_SAMPLE_CONSTRAINED"
    if is_unavailable(state_status) or is_unavailable(transition_status):
        return "STATE_TRANSITION_BASELINE_UNAVAILABLE"
    if is_unavailable(state_dispersion) or is_unavailable(transition_dispersion):
        return "STATE_TRANSITION_MIXED_DIAGNOSTICS"
    if state_status != transition_status or state_dispersion != transition_dispersion:
        return "STATE_TRANSITION_MIXED_DIAGNOSTICS"
    return "STATE_TRANSITION_INCONCLUSIVE"


def _diagnostic(alignment: str) -> str:
    diagnostics = {
        "STATE_TRANSITION_ALIGNED_SCENARIO_SENSITIVE": "State and transition diagnostics both indicate scenario-level sensitivity.",
        "STATE_TRANSITION_ALIGNED_SAMPLE_CONSTRAINED": "State or transition context is sample constrained.",
        "STATE_TRANSITION_MIXED_DIAGNOSTICS": "State and transition diagnostics do not describe the same limitation type.",
        "STATE_TRANSITION_BASELINE_UNAVAILABLE": "Required baseline state or transition diagnostics are unavailable.",
        "STATE_TRANSITION_INCONCLUSIVE": "Available descriptive inputs do not support a stronger alignment class.",
    }
    return diagnostics[alignment]
