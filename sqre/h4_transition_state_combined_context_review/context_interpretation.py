"""Combined context interpretation matrix."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.models import (
    AlignmentReviewRow,
    CombinedContextInterpretationRow,
    CombinedContextInventoryRow,
    CombinedDispersionReviewRow,
    CombinedSensitivityReviewRow,
    PartialContextCaveatRow,
)


def build_context_interpretation_matrix(
    inventory: list[CombinedContextInventoryRow],
    alignment: list[AlignmentReviewRow],
    dispersion: list[CombinedDispersionReviewRow],
    sensitivity: list[CombinedSensitivityReviewRow],
    partial: list[PartialContextCaveatRow],
) -> list[CombinedContextInterpretationRow]:
    alignment_by_id = {row.context_id: row for row in alignment}
    dispersion_by_id = {row.context_id: row for row in dispersion}
    sensitivity_by_id = {row.context_id: row for row in sensitivity}
    partial_by_id = {row.context_id: row for row in partial}
    return [
        _build_row(
            row,
            alignment_by_id[row.context_id],
            dispersion_by_id[row.context_id],
            sensitivity_by_id[row.context_id],
            partial_by_id[row.context_id],
        )
        for row in inventory
    ]


def _build_row(
    inventory: CombinedContextInventoryRow,
    alignment: AlignmentReviewRow,
    dispersion: CombinedDispersionReviewRow,
    sensitivity: CombinedSensitivityReviewRow,
    partial: PartialContextCaveatRow,
) -> CombinedContextInterpretationRow:
    interpretation = _interpretation_class(alignment, dispersion, sensitivity, partial)
    readiness = _readiness_flag(interpretation)
    return CombinedContextInterpretationRow(
        context_id=inventory.context_id,
        symbol=inventory.symbol,
        timeframe=inventory.timeframe,
        source_state=inventory.source_state,
        target_state=inventory.target_state,
        transition_label=inventory.transition_label,
        forward_window=inventory.forward_window,
        state_transition_alignment_class=alignment.state_transition_alignment_class,
        combined_dispersion_class=dispersion.combined_dispersion_class,
        combined_sensitivity_class=sensitivity.combined_sensitivity_class,
        partial_context_use_class=partial.partial_context_use_class,
        combined_context_interpretation_class=interpretation,
        combined_context_readiness_flag=readiness,
        combined_context_diagnostic=_diagnostic(interpretation),
        recommended_follow_up=_follow_up(readiness),
    )


def _interpretation_class(
    alignment: AlignmentReviewRow,
    dispersion: CombinedDispersionReviewRow,
    sensitivity: CombinedSensitivityReviewRow,
    partial: PartialContextCaveatRow,
) -> str:
    if (
        sensitivity.combined_sensitivity_class == "COMBINED_SCENARIO_SENSITIVE"
        or alignment.state_transition_alignment_class == "STATE_TRANSITION_ALIGNED_SCENARIO_SENSITIVE"
    ):
        return "CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION"
    if dispersion.combined_dispersion_class == "COMBINED_HIGH_DISPERSION" and partial.partial_context_use_class in {
        "PARTIAL_CONTEXT_LIMITED_SUPPORT",
        "PARTIAL_CONTEXT_CAVEATED_CONSISTENCY",
    }:
        return "CONTEXT_CONSISTENT_BUT_DISPERSED"
    if (
        dispersion.combined_dispersion_class == "COMBINED_SAMPLE_CONSTRAINED"
        or alignment.state_transition_alignment_class == "STATE_TRANSITION_ALIGNED_SAMPLE_CONSTRAINED"
    ):
        return "CONTEXT_SAMPLE_CONSTRAINED"
    if (
        dispersion.combined_dispersion_class == "COMBINED_BASELINE_UNAVAILABLE"
        or sensitivity.combined_sensitivity_class == "COMBINED_BASELINE_UNAVAILABLE"
    ):
        return "CONTEXT_INPUT_LIMITED"
    if (
        dispersion.combined_dispersion_class == "COMBINED_STABLE_DESCRIPTIVE"
        and sensitivity.combined_sensitivity_class == "COMBINED_NOT_SCENARIO_SENSITIVE_DESCRIPTIVE"
    ):
        return "CONTEXT_DESCRIPTIVELY_STABLE"
    return "CONTEXT_INCONCLUSIVE"


def _readiness_flag(interpretation: str) -> str:
    mapping = {
        "CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION": "REQUIRES_SCENARIO_LEVEL_INTERPRETATION",
        "CONTEXT_CONSISTENT_BUT_DISPERSED": "READY_FOR_DESCRIPTIVE_CONTEXT_REFERENCE",
        "CONTEXT_SAMPLE_CONSTRAINED": "REQUIRES_SAMPLE_ADEQUACY_REVIEW",
        "CONTEXT_INPUT_LIMITED": "REQUIRES_INPUT_COMPLETENESS_REVIEW",
        "CONTEXT_DESCRIPTIVELY_STABLE": "READY_FOR_DESCRIPTIVE_CONTEXT_REFERENCE",
        "CONTEXT_INCONCLUSIVE": "NOT_READY_FOR_CONTEXT_REFERENCE",
    }
    return mapping[interpretation]


def _diagnostic(interpretation: str) -> str:
    diagnostics = {
        "CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION": "Combined state and transition context reinforces scenario-level interpretation.",
        "CONTEXT_CONSISTENT_BUT_DISPERSED": "Combined context is consistent but dispersion remains elevated.",
        "CONTEXT_SAMPLE_CONSTRAINED": "Combined context requires sample adequacy review.",
        "CONTEXT_INPUT_LIMITED": "Combined context is limited by missing baseline inputs.",
        "CONTEXT_DESCRIPTIVELY_STABLE": "Combined context is descriptively stable.",
        "CONTEXT_INCONCLUSIVE": "Combined context remains inconclusive.",
    }
    return diagnostics[interpretation]


def _follow_up(readiness: str) -> str:
    mapping = {
        "READY_FOR_DESCRIPTIVE_CONTEXT_REFERENCE": "Research reference-store design",
        "REQUIRES_SCENARIO_LEVEL_INTERPRETATION": "H4/D1 contextual transition review",
        "REQUIRES_SAMPLE_ADEQUACY_REVIEW": "Provider history coverage review",
        "REQUIRES_INPUT_COMPLETENESS_REVIEW": "Manual H4 baseline input completeness review",
        "NOT_READY_FOR_CONTEXT_REFERENCE": "H1 secondary context monitoring",
    }
    return mapping[readiness]
