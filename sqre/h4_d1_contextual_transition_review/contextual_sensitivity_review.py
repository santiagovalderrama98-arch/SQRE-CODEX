"""Contextual sensitivity review."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.models import (
    ContextualSensitivityReviewRow,
    D1RegimeContextReviewRow,
    H4D1ContextInventoryRow,
)


def build_contextual_sensitivity_review(
    inventory: list[H4D1ContextInventoryRow],
    regime_reviews: list[D1RegimeContextReviewRow],
) -> list[ContextualSensitivityReviewRow]:
    d1_by_id = {row.context_id: row for row in regime_reviews}
    has_grouping = len({row.d1_regime_label for row in regime_reviews if row.d1_regime_label != "D1_CONTEXT_UNMAPPED"}) >= 1
    return [_build_row(row, d1_by_id[row.context_id], has_grouping) for row in inventory]


def _build_row(
    row: H4D1ContextInventoryRow,
    d1: D1RegimeContextReviewRow,
    has_grouping: bool,
) -> ContextualSensitivityReviewRow:
    sensitivity = _classify(row, d1, has_grouping)
    return ContextualSensitivityReviewRow(
        context_id=row.context_id,
        h4_combined_sensitivity_class=row.h4_combined_sensitivity_class,
        d1_regime_sensitivity_class=d1.d1_regime_sensitivity_class,
        d1_regime_label=d1.d1_regime_label,
        contextual_sensitivity_class=sensitivity,
        contextual_sensitivity_diagnostic=_diagnostic(sensitivity),
    )


def _classify(row: H4D1ContextInventoryRow, d1: D1RegimeContextReviewRow, has_grouping: bool) -> str:
    if d1.d1_context_interpretation_class in {"D1_CONTEXT_INPUT_LIMITED", "D1_CONTEXT_UNAVAILABLE"}:
        return "D1_CONTEXT_INPUT_LIMITED"
    if d1.d1_context_interpretation_class == "D1_CONTEXT_SAMPLE_CONSTRAINED":
        return "D1_CONTEXT_SAMPLE_CONSTRAINED"
    h4_sensitive = "SCENARIO" in row.h4_combined_sensitivity_class.upper() or "SCENARIO" in row.h4_context_readiness_flag.upper()
    d1_sensitive = d1.d1_regime_sensitivity_class == "D1_REGIME_SENSITIVE"
    if h4_sensitive and d1_sensitive:
        return "D1_REINFORCES_H4_SCENARIO_SENSITIVITY"
    if h4_sensitive and has_grouping:
        return "D1_CONTEXTUALIZES_H4_SCENARIO_SENSITIVITY"
    if h4_sensitive:
        return "D1_DOES_NOT_RESOLVE_H4_SENSITIVITY"
    return "D1_CONTEXT_INCONCLUSIVE"


def _diagnostic(sensitivity: str) -> str:
    diagnostics = {
        "D1_REINFORCES_H4_SCENARIO_SENSITIVITY": "D1 context reinforces H4 scenario-sensitive descriptive interpretation.",
        "D1_CONTEXTUALIZES_H4_SCENARIO_SENSITIVITY": "D1 context groups H4 scenario-sensitive behavior for descriptive review.",
        "D1_DOES_NOT_RESOLVE_H4_SENSITIVITY": "D1 context does not resolve H4 scenario sensitivity.",
        "D1_CONTEXT_SAMPLE_CONSTRAINED": "D1 context sensitivity review is sample constrained.",
        "D1_CONTEXT_INPUT_LIMITED": "D1 context sensitivity review is input limited.",
        "D1_CONTEXT_INCONCLUSIVE": "D1 context sensitivity review remains inconclusive.",
    }
    return diagnostics[sensitivity]
