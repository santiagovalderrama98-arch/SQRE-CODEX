"""Combined state/transition dispersion review."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.classification import (
    is_high,
    is_moderate,
    is_sample_constrained,
    is_stable,
    is_unavailable,
)
from sqre.h4_transition_state_combined_context_review.models import (
    CombinedContextInventoryRow,
    CombinedDispersionReviewRow,
)


def build_combined_dispersion_review(rows: list[CombinedContextInventoryRow]) -> list[CombinedDispersionReviewRow]:
    return [_build_row(row) for row in rows]


def _build_row(row: CombinedContextInventoryRow) -> CombinedDispersionReviewRow:
    combined_class, driver = _classify(row.state_dispersion_status, row.transition_dispersion_status)
    return CombinedDispersionReviewRow(
        context_id=row.context_id,
        source_state=row.source_state,
        target_state=row.target_state,
        transition_label=row.transition_label,
        forward_window=row.forward_window,
        state_dispersion_class=row.state_dispersion_status,
        transition_dispersion_class=row.transition_dispersion_status,
        combined_dispersion_class=combined_class,
        combined_dispersion_driver=driver,
        combined_dispersion_diagnostic=_diagnostic(combined_class, driver),
    )


def _classify(state: str, transition: str) -> tuple[str, str]:
    if is_unavailable(state) or is_unavailable(transition):
        return "COMBINED_BASELINE_UNAVAILABLE", "INPUT_LIMITED"
    if is_sample_constrained(state) or is_sample_constrained(transition):
        return "COMBINED_SAMPLE_CONSTRAINED", "SAMPLE_DRIVEN"
    if is_high(state) and is_high(transition):
        return "COMBINED_HIGH_DISPERSION", "MIXED_DRIVEN"
    if is_high(state):
        return "COMBINED_HIGH_DISPERSION", "STATE_DRIVEN"
    if is_high(transition):
        return "COMBINED_HIGH_DISPERSION", "TRANSITION_DRIVEN"
    if is_moderate(state) or is_moderate(transition):
        return "COMBINED_MODERATE_DISPERSION", "MIXED_DRIVEN"
    if is_stable(state) and is_stable(transition):
        return "COMBINED_STABLE_DESCRIPTIVE", "MIXED_DRIVEN"
    return "COMBINED_INCONCLUSIVE", "INPUT_LIMITED"


def _diagnostic(combined_class: str, driver: str) -> str:
    return f"{combined_class} identified from descriptive state and transition dispersion inputs; driver={driver}."
