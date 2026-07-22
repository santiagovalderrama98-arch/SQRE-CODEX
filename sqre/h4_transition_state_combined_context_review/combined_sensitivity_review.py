"""Combined state/transition scenario sensitivity review."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.classification import (
    is_high,
    is_sample_constrained,
    is_unavailable,
)
from sqre.h4_transition_state_combined_context_review.models import (
    CombinedContextInventoryRow,
    CombinedSensitivityReviewRow,
)


def build_combined_sensitivity_review(rows: list[CombinedContextInventoryRow]) -> list[CombinedSensitivityReviewRow]:
    return [_build_row(row) for row in rows]


def _build_row(row: CombinedContextInventoryRow) -> CombinedSensitivityReviewRow:
    combined_class = _classify(row.state_sensitivity_status, row.transition_sensitivity_status)
    return CombinedSensitivityReviewRow(
        context_id=row.context_id,
        source_state=row.source_state,
        target_state=row.target_state,
        transition_label=row.transition_label,
        forward_window=row.forward_window,
        state_sensitivity_class=row.state_sensitivity_status,
        transition_sensitivity_class=row.transition_sensitivity_status,
        near_aggregation_candidate_flag="false",
        combined_sensitivity_class=combined_class,
        combined_sensitivity_diagnostic=_diagnostic(combined_class),
    )


def _classify(state: str, transition: str) -> str:
    if is_sample_constrained(state) or is_sample_constrained(transition):
        return "COMBINED_SAMPLE_CONSTRAINED"
    if is_unavailable(state) or is_unavailable(transition):
        return "COMBINED_BASELINE_UNAVAILABLE"
    if is_high(state) and is_high(transition):
        return "COMBINED_SCENARIO_SENSITIVE"
    if is_high(state) or is_high(transition):
        return "COMBINED_PARTIALLY_SCENARIO_SENSITIVE"
    return "COMBINED_NOT_SCENARIO_SENSITIVE_DESCRIPTIVE"


def _diagnostic(combined_class: str) -> str:
    diagnostics = {
        "COMBINED_SCENARIO_SENSITIVE": "State and transition sensitivity diagnostics both require scenario-level interpretation.",
        "COMBINED_PARTIALLY_SCENARIO_SENSITIVE": "Only one side of the combined context shows scenario-level sensitivity.",
        "COMBINED_NOT_SCENARIO_SENSITIVE_DESCRIPTIVE": "Available sensitivity diagnostics do not show scenario-level sensitivity.",
        "COMBINED_SAMPLE_CONSTRAINED": "Sensitivity interpretation is limited by sample constraints.",
        "COMBINED_BASELINE_UNAVAILABLE": "Required sensitivity baseline inputs are unavailable.",
        "COMBINED_INCONCLUSIVE": "Sensitivity inputs are inconclusive.",
    }
    return diagnostics.get(combined_class, diagnostics["COMBINED_INCONCLUSIVE"])
