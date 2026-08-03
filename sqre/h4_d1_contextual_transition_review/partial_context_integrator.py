"""Partial H4 sample context integration."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.loader import first_row, read_optional_csv, text_value
from sqre.h4_d1_contextual_transition_review.models import H4D1ContextInventoryRow, PartialContextIntegrationRow


def partial_context_status(config: H4D1ContextualTransitionReviewConfig) -> str:
    if not config.allow_partial_context:
        return "PARTIAL_CONTEXT_NOT_USED"
    summary = first_row(read_optional_csv(config.partial_complement_dir / "h4_partial_complementary_dispersion_summary.csv"))
    return "PARTIAL_CONTEXT_AVAILABLE" if summary is not None else "PARTIAL_CONTEXT_UNAVAILABLE"


def build_partial_context_integration(
    rows: list[H4D1ContextInventoryRow],
    config: H4D1ContextualTransitionReviewConfig,
) -> list[PartialContextIntegrationRow]:
    summary = first_row(read_optional_csv(config.partial_complement_dir / "h4_partial_complementary_dispersion_summary.csv"))
    caveat = first_row(read_optional_csv(config.partial_complement_dir / "h4_partial_sample_caveat_review.csv"))
    return [_build_row(row, summary, caveat, config) for row in rows]


def _build_row(row: H4D1ContextInventoryRow, summary, caveat, config: H4D1ContextualTransitionReviewConfig) -> PartialContextIntegrationRow:
    interpretation = text_value(summary, ["Dominant_Partial_Baseline_Interpretation"], "PARTIAL_CONTEXT_UNAVAILABLE")
    readiness = text_value(summary, ["H4_Partial_Complementary_Readiness_Flag"], "PARTIAL_CONTEXT_UNAVAILABLE")
    context_use = text_value(caveat, ["Partial_Context_Use_Class"], "PARTIAL_CONTEXT_UNAVAILABLE")
    use_class = _use_class(interpretation, readiness, context_use, config.allow_partial_context)
    return PartialContextIntegrationRow(
        context_id=row.context_id,
        partial_sample_id=text_value(summary, ["Partial_Sample_ID", "Candidate_ID"], "eurusd_h4_period_5_partial"),
        partial_sample_label=config.partial_sample_label,
        partial_interpretation_class=interpretation,
        partial_readiness_flag=readiness,
        partial_context_use_class=context_use,
        h4_d1_partial_use_class=use_class,
        partial_context_diagnostic=_diagnostic(use_class),
    )


def _use_class(interpretation: str, readiness: str, context_use: str, allowed: bool) -> str:
    if not allowed:
        return "PARTIAL_CONTEXT_NOT_USED"
    core_text = f"{interpretation} {readiness}".upper()
    context_text = str(context_use).upper()
    if ("UNAVAILABLE" in core_text or "MISSING" in core_text) and (
        "UNAVAILABLE" in context_text or "MISSING" in context_text
    ):
        return "PARTIAL_CONTEXT_UNAVAILABLE"
    text = f"{core_text} {context_text}"
    if "LIMIT" in text or "CONSISTENT" in text:
        return "PARTIAL_CONTEXT_LIMITED_COMPLEMENT"
    if "CAVEAT" in text or "REFERENCE" in text:
        return "PARTIAL_CONTEXT_CAVEATED_REFERENCE"
    return "PARTIAL_CONTEXT_NOT_USED"


def _diagnostic(use_class: str) -> str:
    diagnostics = {
        "PARTIAL_CONTEXT_LIMITED_COMPLEMENT": "Partial H4 sample is used only as limited complementary evidence.",
        "PARTIAL_CONTEXT_CAVEATED_REFERENCE": "Partial H4 sample is available with caveats.",
        "PARTIAL_CONTEXT_NOT_USED": "Partial H4 sample is not included in contextual interpretation.",
        "PARTIAL_CONTEXT_UNAVAILABLE": "Partial H4 sample context is unavailable.",
    }
    return diagnostics[use_class]
