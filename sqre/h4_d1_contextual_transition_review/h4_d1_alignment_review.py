"""H4/D1 alignment review."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.models import (
    D1RegimeContextReviewRow,
    H4D1AlignmentReviewRow,
    H4D1ContextInventoryRow,
)


def build_h4_d1_alignment_review(
    inventory: list[H4D1ContextInventoryRow],
    regime_reviews: list[D1RegimeContextReviewRow],
) -> list[H4D1AlignmentReviewRow]:
    regime_by_id = {row.context_id: row for row in regime_reviews}
    return [_build_row(row, regime_by_id[row.context_id]) for row in inventory]


def _build_row(row: H4D1ContextInventoryRow, d1: D1RegimeContextReviewRow) -> H4D1AlignmentReviewRow:
    alignment = _classify(row, d1)
    return H4D1AlignmentReviewRow(
        context_id=row.context_id,
        h4_source_state=row.h4_source_state,
        h4_target_state=row.h4_target_state,
        h4_transition_label=row.h4_transition_label,
        h4_forward_window=row.h4_forward_window,
        h4_context_interpretation_class=row.h4_context_interpretation_class,
        h4_context_readiness_flag=row.h4_context_readiness_flag,
        d1_context_interpretation_class=d1.d1_context_interpretation_class,
        d1_regime_label=d1.d1_regime_label,
        h4_d1_alignment_class=alignment,
        h4_d1_alignment_diagnostic=_diagnostic(alignment),
    )


def _classify(row: H4D1ContextInventoryRow, d1: D1RegimeContextReviewRow) -> str:
    if row.mapping_confidence_class in {"LOW_CONFIDENCE_MAPPING", "NO_CONFIDENCE_MAPPING"}:
        return "H4_D1_MAPPING_LIMITED"
    if d1.d1_context_interpretation_class in {"D1_CONTEXT_INPUT_LIMITED", "D1_CONTEXT_UNAVAILABLE", "D1_CONTEXT_SAMPLE_CONSTRAINED"}:
        return "H4_D1_D1_CONTEXT_LIMITED"
    if _scenario_level(row) and d1.d1_context_interpretation_class == "D1_CONTEXT_REGIME_SENSITIVE":
        return "H4_D1_ALIGNED_SCENARIO_AND_REGIME_SENSITIVE"
    if _dispersed(row) and d1.d1_context_interpretation_class == "D1_CONTEXT_REGIME_SENSITIVE":
        return "H4_D1_ALIGNED_DISPERSED_CONTEXT"
    if _scenario_level(row) and d1.d1_context_interpretation_class == "D1_CONTEXT_DESCRIPTIVE_REFERENCE":
        return "H4_D1_MIXED_CONTEXT"
    return "H4_D1_INCONCLUSIVE"


def _scenario_level(row: H4D1ContextInventoryRow) -> bool:
    text = f"{row.h4_context_interpretation_class} {row.h4_context_readiness_flag}".upper()
    return "SCENARIO" in text


def _dispersed(row: H4D1ContextInventoryRow) -> bool:
    text = f"{row.h4_context_interpretation_class} {row.h4_combined_dispersion_class}".upper()
    return "DISPER" in text or "HIGH" in text


def _diagnostic(alignment: str) -> str:
    diagnostics = {
        "H4_D1_ALIGNED_SCENARIO_AND_REGIME_SENSITIVE": "H4 scenario-level context aligns with D1 regime-sensitive context.",
        "H4_D1_ALIGNED_DISPERSED_CONTEXT": "H4 dispersed context aligns with D1 dispersed or regime-sensitive context.",
        "H4_D1_MIXED_CONTEXT": "H4 and D1 context diagnostics point to different limitation types.",
        "H4_D1_D1_CONTEXT_LIMITED": "D1 contextual layer is limited.",
        "H4_D1_MAPPING_LIMITED": "H4/D1 scenario or regime mapping is limited.",
        "H4_D1_INCONCLUSIVE": "H4/D1 alignment remains inconclusive.",
    }
    return diagnostics[alignment]
