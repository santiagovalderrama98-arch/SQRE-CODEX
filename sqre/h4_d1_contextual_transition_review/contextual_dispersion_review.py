"""Contextual dispersion review."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.models import (
    ContextualDispersionReviewRow,
    D1RegimeContextReviewRow,
    H4D1ContextInventoryRow,
)


def build_contextual_dispersion_review(
    inventory: list[H4D1ContextInventoryRow],
    regime_reviews: list[D1RegimeContextReviewRow],
) -> list[ContextualDispersionReviewRow]:
    d1_by_id = {row.context_id: row for row in regime_reviews}
    regime_count = len({row.d1_regime_label for row in regime_reviews if row.d1_regime_label != "D1_CONTEXT_UNMAPPED"})
    return [_build_row(row, d1_by_id[row.context_id], regime_count) for row in inventory]


def _build_row(
    row: H4D1ContextInventoryRow,
    d1: D1RegimeContextReviewRow,
    regime_count: int,
) -> ContextualDispersionReviewRow:
    dispersion_class, driver = _classify(row, d1, regime_count)
    return ContextualDispersionReviewRow(
        context_id=row.context_id,
        h4_transition_label=row.h4_transition_label,
        h4_forward_window=row.h4_forward_window,
        h4_combined_dispersion_class=row.h4_combined_dispersion_class,
        d1_dispersion_class=d1.d1_dispersion_class,
        d1_regime_label=d1.d1_regime_label,
        contextual_dispersion_class=dispersion_class,
        contextual_dispersion_driver=driver,
        contextual_dispersion_diagnostic=_diagnostic(dispersion_class, driver),
    )


def _classify(row: H4D1ContextInventoryRow, d1: D1RegimeContextReviewRow, regime_count: int) -> tuple[str, str]:
    if d1.d1_context_interpretation_class in {"D1_CONTEXT_INPUT_LIMITED", "D1_CONTEXT_UNAVAILABLE"}:
        return "D1_CONTEXT_INPUT_LIMITED", "INPUT_LIMITED"
    if d1.d1_context_interpretation_class == "D1_CONTEXT_SAMPLE_CONSTRAINED":
        return "D1_CONTEXT_SAMPLE_CONSTRAINED", "SAMPLE_DRIVEN"
    if _high(row.h4_combined_dispersion_class) and (_high(d1.d1_dispersion_class) or "REGIME_SENSITIVE" in d1.d1_regime_sensitivity_class):
        return "D1_CONTEXT_REINFORCES_H4_DISPERSION", "MIXED_H4_D1_DRIVEN"
    if regime_count >= 2 and row.mapping_confidence_class in {"HIGH_CONFIDENCE_MAPPING", "MODERATE_CONFIDENCE_MAPPING"}:
        return "D1_CONTEXT_SEGMENTS_H4_DISPERSION", "D1_DRIVEN"
    if _high(row.h4_combined_dispersion_class):
        return "D1_CONTEXT_DOES_NOT_REDUCE_H4_DISPERSION", "H4_DRIVEN"
    return "D1_CONTEXT_INCONCLUSIVE", "INPUT_LIMITED"


def _diagnostic(dispersion_class: str, driver: str) -> str:
    return f"{dispersion_class} from descriptive H4/D1 context review; driver={driver}."


def _high(value: str) -> bool:
    text = str(value).upper()
    return "HIGH" in text or "DISPER" in text
