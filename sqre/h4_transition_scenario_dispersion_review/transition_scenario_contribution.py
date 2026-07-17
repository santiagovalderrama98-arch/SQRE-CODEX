"""Scenario contribution summaries."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_transition_scenario_dispersion_review.classification import dominant_deviation_class, scenario_contribution_class
from sqre.h4_transition_scenario_dispersion_review.config import H4TransitionScenarioDispersionReviewConfig
from sqre.h4_transition_scenario_dispersion_review.findings import scenario_diagnostic
from sqre.h4_transition_scenario_dispersion_review.models import ScenarioComparisonInput, ScenarioContributionRow
from sqre.h4_transition_scenario_dispersion_review.transition_family_dispersion import mean


def build_scenario_contributions(
    comparisons: list[ScenarioComparisonInput],
    config: H4TransitionScenarioDispersionReviewConfig,
) -> list[ScenarioContributionRow]:
    grouped: dict[str, list[ScenarioComparisonInput]] = defaultdict(list)
    for row in comparisons:
        grouped[row.scenario_id].append(row)

    rows: list[ScenarioContributionRow] = []
    for scenario_id, items in sorted(grouped.items()):
        high = _count(items, "HIGH_DEVIATION")
        moderate = _count(items, "MODERATE_DEVIATION")
        low = _count(items, "LOW_DEVIATION")
        ratio = high / len(items) if items else 0.0
        contribution = scenario_contribution_class(ratio, config)
        rows.append(
            ScenarioContributionRow(
                scenario_id=scenario_id,
                profile_count=len({(item.condition_label, item.forward_window) for item in items}),
                total_observations=len(items),
                average_sample_size=mean([item.sample_size for item in items]),
                average_forward_range_deviation=mean([abs(item.forward_range_vs_profile_avg) for item in items]),
                average_outcome_magnitude_deviation=mean([abs(item.outcome_magnitude_vs_profile_avg) for item in items]),
                average_direction_alignment_deviation=mean([abs(item.direction_alignment_vs_profile_avg) for item in items]),
                high_deviation_profile_count=high,
                moderate_deviation_profile_count=moderate,
                low_deviation_profile_count=low,
                high_deviation_profile_ratio=ratio,
                dominant_deviation_class=dominant_deviation_class([item.scenario_deviation_class for item in items]),
                scenario_contribution_class=contribution,
                scenario_dispersion_diagnostic=scenario_diagnostic(contribution),
            )
        )
    return rows


def _count(rows: list[ScenarioComparisonInput], deviation_class: str) -> int:
    return sum(1 for row in rows if row.scenario_deviation_class == deviation_class)
