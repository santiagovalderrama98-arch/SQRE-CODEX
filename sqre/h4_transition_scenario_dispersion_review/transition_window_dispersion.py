"""Forward-window dispersion summaries for H4 transition profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_transition_scenario_dispersion_review.findings import window_diagnostic, window_follow_up
from sqre.h4_transition_scenario_dispersion_review.models import (
    ForwardWindowDispersionSummaryRow,
    ProfileDispersionDiagnostic,
)
from sqre.h4_transition_scenario_dispersion_review.transition_family_dispersion import mean


def build_transition_window_dispersion_summary(
    rows: list[ProfileDispersionDiagnostic],
) -> list[ForwardWindowDispersionSummaryRow]:
    grouped: dict[int, list[ProfileDispersionDiagnostic]] = defaultdict(list)
    for row in rows:
        grouped[row.forward_window].append(row)

    summaries: list[ForwardWindowDispersionSummaryRow] = []
    for window, items in sorted(grouped.items()):
        high = _count_dispersion(items, "HIGH_DISPERSION")
        moderate = _count_dispersion(items, "MODERATE_DISPERSION")
        stable = _count_dispersion(items, "STABLE_DESCRIPTIVE")
        summaries.append(
            ForwardWindowDispersionSummaryRow(
                forward_window=window,
                profile_count=len(items),
                research_ready_profile_count=sum(1 for item in items if item.profile_type == "RESEARCH_READY"),
                scenario_sensitive_profile_count=_count_readiness(items, "SCENARIO_SENSITIVE_REVIEW"),
                sample_constrained_profile_count=_count_readiness(items, "SAMPLE_REVIEW"),
                aggregation_candidate_profile_count=_count_readiness(items, "AGGREGATION_CANDIDATE"),
                high_dispersion_profile_count=high,
                moderate_dispersion_profile_count=moderate,
                stable_profile_count=stable,
                average_forward_range_cv=mean([item.forward_range_cv for item in items]),
                average_outcome_magnitude_cv=mean([item.outcome_magnitude_cv for item in items]),
                average_direction_alignment_dispersion=mean([item.direction_alignment_dispersion for item in items]),
                average_high_deviation_scenario_count=mean([item.high_deviation_scenario_count for item in items]),
                window_dispersion_diagnostic=window_diagnostic(len(items), high, stable, moderate),
                recommended_follow_up=window_follow_up(high),
            )
        )
    return summaries


def _count_dispersion(rows: list[ProfileDispersionDiagnostic], dispersion_class: str) -> int:
    return sum(1 for row in rows if row.profile_dispersion_class == dispersion_class)


def _count_readiness(rows: list[ProfileDispersionDiagnostic], readiness_class: str) -> int:
    return sum(1 for row in rows if row.transition_profile_readiness_class == readiness_class)
