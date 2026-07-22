"""Integrate partial sample caveats into combined context rows."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.models import (
    CombinedContextInventoryRow,
    PartialContext,
    PartialContextCaveatRow,
)


def build_partial_caveat_integration(
    rows: list[CombinedContextInventoryRow],
    partial: PartialContext,
) -> list[PartialContextCaveatRow]:
    return [_build_row(row, partial) for row in rows]


def _build_row(row: CombinedContextInventoryRow, partial: PartialContext) -> PartialContextCaveatRow:
    use_class = _classify(partial)
    return PartialContextCaveatRow(
        context_id=row.context_id,
        partial_sample_id=partial.partial_sample_id,
        partial_sample_label=partial.partial_sample_label,
        partial_interpretation_class=partial.partial_interpretation_class,
        partial_readiness_flag=partial.partial_readiness_flag,
        partial_caveat_class=partial.partial_caveat_class,
        partial_context_use_class=use_class,
        partial_context_diagnostic=_diagnostic(use_class),
    )


def _classify(partial: PartialContext) -> str:
    interpretation = partial.partial_interpretation_class.upper()
    readiness = partial.partial_readiness_flag.upper()
    caveat = partial.partial_caveat_class.upper()
    if interpretation == "PARTIAL_CONTEXT_UNAVAILABLE":
        return "PARTIAL_CONTEXT_UNAVAILABLE"
    if (
        interpretation == "COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED"
        and readiness == "PARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION"
    ):
        return "PARTIAL_CONTEXT_LIMITED_SUPPORT"
    if "CONSISTENT" in interpretation and ("ACCEPTABLE" in caveat or "LIMITED" in readiness):
        return "PARTIAL_CONTEXT_CAVEATED_CONSISTENCY"
    if "UNAVAILABLE" in interpretation or "NOT" in interpretation:
        return "PARTIAL_CONTEXT_NOT_USABLE"
    return "PARTIAL_CONTEXT_NOT_USABLE"


def _diagnostic(use_class: str) -> str:
    diagnostics = {
        "PARTIAL_CONTEXT_LIMITED_SUPPORT": "Partial sample context is consistent but requires limited interpretation.",
        "PARTIAL_CONTEXT_CAVEATED_CONSISTENCY": "Partial sample context is caveated but directionally consistent with baseline diagnostics.",
        "PARTIAL_CONTEXT_NOT_USABLE": "Partial sample context is not usable for this descriptive review.",
        "PARTIAL_CONTEXT_UNAVAILABLE": "Partial sample context files were unavailable.",
    }
    return diagnostics[use_class]
