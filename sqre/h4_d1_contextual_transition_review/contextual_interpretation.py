"""Final H4/D1 contextual interpretation matrix."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.models import (
    ContextualDispersionReviewRow,
    ContextualSensitivityReviewRow,
    H4D1AlignmentReviewRow,
    H4D1ContextInventoryRow,
    H4D1ContextualInterpretationRow,
    PartialContextIntegrationRow,
)


def build_contextual_interpretation_matrix(
    inventory: list[H4D1ContextInventoryRow],
    alignment: list[H4D1AlignmentReviewRow],
    dispersion: list[ContextualDispersionReviewRow],
    sensitivity: list[ContextualSensitivityReviewRow],
    partial: list[PartialContextIntegrationRow],
) -> list[H4D1ContextualInterpretationRow]:
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
    inventory: H4D1ContextInventoryRow,
    alignment: H4D1AlignmentReviewRow,
    dispersion: ContextualDispersionReviewRow,
    sensitivity: ContextualSensitivityReviewRow,
    partial: PartialContextIntegrationRow,
) -> H4D1ContextualInterpretationRow:
    interpretation = _interpretation(alignment, dispersion, sensitivity)
    readiness = _readiness(interpretation)
    return H4D1ContextualInterpretationRow(
        context_id=inventory.context_id,
        symbol=inventory.symbol,
        h4_timeframe=inventory.h4_timeframe,
        d1_timeframe=inventory.d1_timeframe,
        h4_source_state=inventory.h4_source_state,
        h4_target_state=inventory.h4_target_state,
        h4_transition_label=inventory.h4_transition_label,
        h4_forward_window=inventory.h4_forward_window,
        d1_regime_label=inventory.d1_regime_label,
        h4_d1_alignment_class=alignment.h4_d1_alignment_class,
        contextual_dispersion_class=dispersion.contextual_dispersion_class,
        contextual_sensitivity_class=sensitivity.contextual_sensitivity_class,
        h4_d1_partial_use_class=partial.h4_d1_partial_use_class,
        h4_d1_contextual_interpretation_class=interpretation,
        h4_d1_contextual_readiness_flag=readiness,
        h4_d1_contextual_diagnostic=_diagnostic(interpretation),
        recommended_follow_up=_follow_up(readiness),
    )


def _interpretation(
    alignment: H4D1AlignmentReviewRow,
    dispersion: ContextualDispersionReviewRow,
    sensitivity: ContextualSensitivityReviewRow,
) -> str:
    if (
        alignment.h4_d1_alignment_class == "H4_D1_ALIGNED_SCENARIO_AND_REGIME_SENSITIVE"
        or sensitivity.contextual_sensitivity_class == "D1_REINFORCES_H4_SCENARIO_SENSITIVITY"
    ):
        return "D1_CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION"
    if dispersion.contextual_dispersion_class == "D1_CONTEXT_SEGMENTS_H4_DISPERSION":
        return "D1_CONTEXT_PROVIDES_LIMITED_SEGMENTATION"
    if dispersion.contextual_dispersion_class in {
        "D1_CONTEXT_REINFORCES_H4_DISPERSION",
        "D1_CONTEXT_DOES_NOT_REDUCE_H4_DISPERSION",
    }:
        return "D1_CONTEXT_REMAINS_DISPERSED"
    if dispersion.contextual_dispersion_class == "D1_CONTEXT_SAMPLE_CONSTRAINED":
        return "D1_CONTEXT_SAMPLE_CONSTRAINED"
    if dispersion.contextual_dispersion_class == "D1_CONTEXT_INPUT_LIMITED":
        return "D1_CONTEXT_INPUT_LIMITED"
    return "D1_CONTEXT_INCONCLUSIVE"


def _readiness(interpretation: str) -> str:
    mapping = {
        "D1_CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION": "REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION",
        "D1_CONTEXT_PROVIDES_LIMITED_SEGMENTATION": "READY_FOR_CONTEXTUAL_DESCRIPTIVE_REFERENCE",
        "D1_CONTEXT_REMAINS_DISPERSED": "REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION",
        "D1_CONTEXT_SAMPLE_CONSTRAINED": "REQUIRES_SAMPLE_ADEQUACY_REVIEW",
        "D1_CONTEXT_INPUT_LIMITED": "REQUIRES_INPUT_COMPLETENESS_REVIEW",
        "D1_CONTEXT_INCONCLUSIVE": "NOT_READY_FOR_CONTEXTUAL_REFERENCE",
    }
    return mapping[interpretation]


def _diagnostic(interpretation: str) -> str:
    diagnostics = {
        "D1_CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION": "D1 context reinforces scenario and regime-level descriptive interpretation.",
        "D1_CONTEXT_PROVIDES_LIMITED_SEGMENTATION": "D1 context provides limited descriptive segmentation.",
        "D1_CONTEXT_REMAINS_DISPERSED": "D1 context does not reduce H4 dispersion.",
        "D1_CONTEXT_SAMPLE_CONSTRAINED": "H4/D1 contextual interpretation requires sample adequacy review.",
        "D1_CONTEXT_INPUT_LIMITED": "H4/D1 contextual interpretation is limited by missing or unmapped inputs.",
        "D1_CONTEXT_INCONCLUSIVE": "H4/D1 contextual interpretation remains inconclusive.",
    }
    return diagnostics[interpretation]


def _follow_up(readiness: str) -> str:
    mapping = {
        "READY_FOR_CONTEXTUAL_DESCRIPTIVE_REFERENCE": "Research reference-store design",
        "REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION": "D1 regime context deepening",
        "REQUIRES_SAMPLE_ADEQUACY_REVIEW": "Manual provider history coverage review",
        "REQUIRES_INPUT_COMPLETENESS_REVIEW": "H4/D1 scenario mapping completeness review",
        "NOT_READY_FOR_CONTEXTUAL_REFERENCE": "H1 secondary context monitoring",
    }
    return mapping[readiness]
