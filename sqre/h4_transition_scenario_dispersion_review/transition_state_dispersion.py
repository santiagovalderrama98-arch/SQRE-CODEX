"""Source-state and target-state dispersion summaries."""

from __future__ import annotations

from sqre.h4_transition_scenario_dispersion_review.models import (
    ProfileDispersionDiagnostic,
    TransitionGroupDispersionSummaryRow,
)
from sqre.h4_transition_scenario_dispersion_review.findings import state_diagnostic
from sqre.h4_transition_scenario_dispersion_review.transition_family_dispersion import build_group_dispersion_summary


def build_source_state_dispersion_summary(
    rows: list[ProfileDispersionDiagnostic],
) -> list[TransitionGroupDispersionSummaryRow]:
    return build_group_dispersion_summary(rows, lambda row: row.source_state, state_diagnostic)


def build_target_state_dispersion_summary(
    rows: list[ProfileDispersionDiagnostic],
) -> list[TransitionGroupDispersionSummaryRow]:
    return build_group_dispersion_summary(rows, lambda row: row.target_state, state_diagnostic)
