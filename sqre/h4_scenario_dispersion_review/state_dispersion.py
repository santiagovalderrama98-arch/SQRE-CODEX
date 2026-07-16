"""State-level dispersion summaries."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_scenario_dispersion_review.findings import state_diagnostic, state_follow_up
from sqre.h4_scenario_dispersion_review.models import ProfileDispersionDiagnostic, StateDispersionSummaryRow
from sqre.h4_scenario_dispersion_review.window_dispersion import mean


def build_state_dispersion_summary(rows: list[ProfileDispersionDiagnostic]) -> list[StateDispersionSummaryRow]:
    grouped: dict[str, list[ProfileDispersionDiagnostic]] = defaultdict(list)
    for row in rows:
        grouped[row.condition_label].append(row)
    summaries: list[StateDispersionSummaryRow] = []
    for label, items in sorted(grouped.items()):
        high = _count_dispersion(items, "HIGH_DISPERSION")
        moderate = _count_dispersion(items, "MODERATE_DISPERSION")
        stable = _count_dispersion(items, "STABLE_DESCRIPTIVE")
        aggregation = _count_readiness(items, "AGGREGATION_CANDIDATE")
        scenario = _count_readiness(items, "SCENARIO_SENSITIVE_REVIEW")
        sample = _count_readiness(items, "SAMPLE_REVIEW")
        summaries.append(
            StateDispersionSummaryRow(
                condition_label=label,
                profile_count=len(items),
                research_ready_profile_count=sum(1 for item in items if item.profile_type == "RESEARCH_READY"),
                sample_constrained_profile_count=sample,
                high_dispersion_profile_count=high,
                moderate_dispersion_profile_count=moderate,
                stable_profile_count=stable,
                average_forward_range_cv=mean([item.forward_range_cv for item in items]),
                average_outcome_magnitude_cv=mean([item.outcome_magnitude_cv for item in items]),
                average_direction_alignment_dispersion=mean([item.direction_alignment_dispersion for item in items]),
                average_high_deviation_scenario_count=mean([item.high_deviation_scenario_count for item in items]),
                dominant_dispersion_class=_dominant_dispersion(high, moderate, stable),
                state_dispersion_diagnostic=state_diagnostic(len(items), aggregation, scenario, sample),
                recommended_follow_up=state_follow_up(scenario, sample),
            )
        )
    return summaries


def _count_dispersion(rows: list[ProfileDispersionDiagnostic], dispersion_class: str) -> int:
    return sum(1 for row in rows if row.profile_dispersion_class == dispersion_class)


def _count_readiness(rows: list[ProfileDispersionDiagnostic], readiness_class: str) -> int:
    return sum(1 for row in rows if row.profile_research_readiness_class == readiness_class)


def _dominant_dispersion(high: int, moderate: int, stable: int) -> str:
    counts = {
        "HIGH_DISPERSION": high,
        "MODERATE_DISPERSION": moderate,
        "STABLE_DESCRIPTIVE": stable,
    }
    priority = ["HIGH_DISPERSION", "MODERATE_DISPERSION", "STABLE_DESCRIPTIVE"]
    return max(priority, key=lambda item: (counts[item], -priority.index(item)))
