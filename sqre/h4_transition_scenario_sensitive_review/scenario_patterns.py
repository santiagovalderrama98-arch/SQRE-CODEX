"""Scenario recurrent deviation summaries for H4 transition review."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_transition_scenario_sensitive_review.findings import scenario_review_diagnostic
from sqre.h4_transition_scenario_sensitive_review.models import (
    ScenarioDeviationDetailRow,
    ScenarioRecurrentDeviationSummary,
)
from sqre.h4_transition_scenario_sensitive_review.profile_selector import most_common
from sqre.h4_transition_scenario_sensitive_review.transition_family_review import mean


def build_scenario_recurrent_deviation_summary(
    details: list[ScenarioDeviationDetailRow],
) -> list[ScenarioRecurrentDeviationSummary]:
    grouped: dict[str, list[ScenarioDeviationDetailRow]] = defaultdict(list)
    for row in details:
        grouped[row.scenario_id].append(row)

    summaries: list[ScenarioRecurrentDeviationSummary] = []
    for scenario_id, items in sorted(grouped.items()):
        high = _count(items, "HIGH_DEVIATION")
        moderate = _count(items, "MODERATE_DEVIATION")
        low = _count(items, "LOW_DEVIATION")
        ratio = high / len(items) if items else 0.0
        recurrent = _scenario_recurrent_deviation_class(ratio)
        summaries.append(
            ScenarioRecurrentDeviationSummary(
                scenario_id=scenario_id,
                scenario_profile_count=len({(item.condition_label, item.forward_window) for item in items}),
                high_deviation_profile_count=high,
                moderate_deviation_profile_count=moderate,
                low_deviation_profile_count=low,
                average_forward_range_deviation=mean([abs(item.forward_range_vs_profile_avg) for item in items]),
                average_outcome_magnitude_deviation=mean([abs(item.outcome_magnitude_vs_profile_avg) for item in items]),
                average_direction_alignment_deviation=mean([abs(item.direction_alignment_vs_profile_avg) for item in items]),
                most_common_primary_deviation_metric=most_common(
                    [item.primary_scenario_deviation_metric for item in items],
                    "MIXED",
                ),
                scenario_recurrent_deviation_class=recurrent,
                scenario_review_diagnostic=scenario_review_diagnostic(recurrent),
            )
        )
    return summaries


def _count(rows: list[ScenarioDeviationDetailRow], deviation_class: str) -> int:
    return sum(1 for row in rows if row.scenario_deviation_class == deviation_class)


def _scenario_recurrent_deviation_class(high_deviation_ratio: float) -> str:
    if high_deviation_ratio >= 0.35:
        return "HIGH_RECURRENT_DEVIATION"
    if high_deviation_ratio >= 0.20:
        return "MODERATE_RECURRENT_DEVIATION"
    return "LOW_RECURRENT_DEVIATION"
