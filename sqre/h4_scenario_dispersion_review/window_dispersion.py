"""Forward-window dispersion summaries."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_scenario_dispersion_review.findings import window_diagnostic, window_follow_up
from sqre.h4_scenario_dispersion_review.models import ProfileDispersionDiagnostic, WindowDispersionSummaryRow


def build_window_dispersion_summary(rows: list[ProfileDispersionDiagnostic]) -> list[WindowDispersionSummaryRow]:
    grouped: dict[int, list[ProfileDispersionDiagnostic]] = defaultdict(list)
    for row in rows:
        grouped[row.forward_window].append(row)
    summaries: list[WindowDispersionSummaryRow] = []
    for window, items in sorted(grouped.items()):
        high = _count_dispersion(items, "HIGH_DISPERSION")
        moderate = _count_dispersion(items, "MODERATE_DISPERSION")
        stable = _count_dispersion(items, "STABLE_DESCRIPTIVE")
        summaries.append(
            WindowDispersionSummaryRow(
                forward_window=window,
                profile_count=len(items),
                research_ready_profile_count=sum(1 for item in items if item.profile_type == "RESEARCH_READY"),
                sample_constrained_profile_count=sum(1 for item in items if item.profile_research_readiness_class == "SAMPLE_REVIEW"),
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


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _count_dispersion(rows: list[ProfileDispersionDiagnostic], dispersion_class: str) -> int:
    return sum(1 for row in rows if row.profile_dispersion_class == dispersion_class)
