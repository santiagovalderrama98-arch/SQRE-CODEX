"""Transition-family dispersion summaries."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from sqre.h4_transition_scenario_dispersion_review.findings import group_diagnostic, group_follow_up
from sqre.h4_transition_scenario_dispersion_review.models import (
    ProfileDispersionDiagnostic,
    TransitionGroupDispersionSummaryRow,
)


def build_transition_family_dispersion_summary(
    rows: list[ProfileDispersionDiagnostic],
) -> list[TransitionGroupDispersionSummaryRow]:
    return build_group_dispersion_summary(rows, lambda row: row.transition_family)


def build_group_dispersion_summary(
    rows: list[ProfileDispersionDiagnostic],
    key_fn: Callable[[ProfileDispersionDiagnostic], str],
    diagnostic_fn: Callable[[int, int, int, int], str] = group_diagnostic,
) -> list[TransitionGroupDispersionSummaryRow]:
    grouped: dict[str, list[ProfileDispersionDiagnostic]] = defaultdict(list)
    for row in rows:
        grouped[key_fn(row)].append(row)
    return [_summary_row(group_value, items, diagnostic_fn) for group_value, items in sorted(grouped.items())]


def _summary_row(
    group_value: str,
    items: list[ProfileDispersionDiagnostic],
    diagnostic_fn: Callable[[int, int, int, int], str],
) -> TransitionGroupDispersionSummaryRow:
    high = _count_dispersion(items, "HIGH_DISPERSION")
    moderate = _count_dispersion(items, "MODERATE_DISPERSION")
    stable = _count_dispersion(items, "STABLE_DESCRIPTIVE")
    aggregation = _count_readiness(items, "AGGREGATION_CANDIDATE")
    scenario = _count_readiness(items, "SCENARIO_SENSITIVE_REVIEW")
    sample = _count_readiness(items, "SAMPLE_REVIEW")
    return TransitionGroupDispersionSummaryRow(
        group_value=group_value,
        profile_count=len(items),
        research_ready_profile_count=sum(1 for item in items if item.profile_type == "RESEARCH_READY"),
        scenario_sensitive_profile_count=scenario,
        sample_constrained_profile_count=sample,
        aggregation_candidate_profile_count=aggregation,
        high_dispersion_profile_count=high,
        moderate_dispersion_profile_count=moderate,
        stable_profile_count=stable,
        average_forward_range_cv=mean([item.forward_range_cv for item in items]),
        average_outcome_magnitude_cv=mean([item.outcome_magnitude_cv for item in items]),
        average_direction_alignment_dispersion=mean([item.direction_alignment_dispersion for item in items]),
        average_high_deviation_scenario_count=mean([item.high_deviation_scenario_count for item in items]),
        dominant_dispersion_class=_dominant_dispersion(high, moderate, stable),
        dispersion_diagnostic=diagnostic_fn(len(items), aggregation, scenario, sample),
        recommended_follow_up=group_follow_up(scenario, sample),
    )


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _count_dispersion(rows: list[ProfileDispersionDiagnostic], dispersion_class: str) -> int:
    return sum(1 for row in rows if row.profile_dispersion_class == dispersion_class)


def _count_readiness(rows: list[ProfileDispersionDiagnostic], readiness_class: str) -> int:
    return sum(1 for row in rows if row.transition_profile_readiness_class == readiness_class)


def _dominant_dispersion(high: int, moderate: int, stable: int) -> str:
    counts = {
        "HIGH_DISPERSION": high,
        "MODERATE_DISPERSION": moderate,
        "STABLE_DESCRIPTIVE": stable,
    }
    priority = ["HIGH_DISPERSION", "MODERATE_DISPERSION", "STABLE_DESCRIPTIVE"]
    return max(priority, key=lambda item: (counts[item], -priority.index(item)))
