"""Profile-level dispersion diagnostics."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_scenario_dispersion_review.classification import (
    dispersion_driver_class,
    dominant_deviation_class,
    profile_dispersion_class,
    profile_research_readiness_class,
)
from sqre.h4_scenario_dispersion_review.config import H4ScenarioDispersionReviewConfig
from sqre.h4_scenario_dispersion_review.findings import profile_diagnostic, profile_follow_up
from sqre.h4_scenario_dispersion_review.models import (
    OutcomeStatisticsInput,
    ProfileDispersionDiagnostic,
    ProfileInventoryRow,
    ScenarioComparisonInput,
)


def build_profile_dispersion_diagnostics(
    profiles: list[ProfileInventoryRow],
    statistics: list[OutcomeStatisticsInput],
    comparisons: list[ScenarioComparisonInput],
    config: H4ScenarioDispersionReviewConfig,
) -> list[ProfileDispersionDiagnostic]:
    profiles_by_key = {(row.condition_label, row.forward_window): row for row in profiles}
    comparisons_by_key: dict[tuple[str, int], list[ScenarioComparisonInput]] = defaultdict(list)
    for row in comparisons:
        comparisons_by_key[(row.condition_label, row.forward_window)].append(row)

    diagnostics: list[ProfileDispersionDiagnostic] = []
    for stat in sorted(statistics, key=lambda item: (item.condition_label, item.forward_window)):
        profile = profiles_by_key.get((stat.condition_label, stat.forward_window))
        profile_type = profile.profile_type if profile else stat.profile_type
        scenario_count = profile.scenario_count if profile and profile.scenario_count else stat.scenario_count
        total_sample_size = profile.total_sample_size if profile and profile.total_sample_size else stat.total_sample_size
        related = comparisons_by_key.get((stat.condition_label, stat.forward_window), [])
        high = _count_deviation(related, "HIGH_DEVIATION")
        moderate = _count_deviation(related, "MODERATE_DEVIATION")
        low = _count_deviation(related, "LOW_DEVIATION")
        dominant = dominant_deviation_class([row.scenario_deviation_class for row in related])
        dispersion = profile_dispersion_class(stat.forward_range_cv, stat.outcome_magnitude_cv, config)
        driver = dispersion_driver_class(stat.forward_range_cv, stat.outcome_magnitude_cv, config)
        readiness = profile_research_readiness_class(
            profile_type=profile_type,
            total_sample_size=total_sample_size,
            scenario_count=scenario_count,
            dispersion_class=dispersion,
            high_deviation_count=high,
            dominant_deviation=dominant,
            config=config,
        )
        diagnostics.append(
            ProfileDispersionDiagnostic(
                condition_label=stat.condition_label,
                forward_window=stat.forward_window,
                profile_type=profile_type,
                scenario_count=scenario_count,
                total_sample_size=total_sample_size,
                average_forward_range_pips=stat.average_forward_range_pips,
                average_outcome_magnitude_pips=stat.average_outcome_magnitude_pips,
                average_direction_alignment_rate=stat.average_direction_alignment_rate,
                forward_range_cv=stat.forward_range_cv,
                outcome_magnitude_cv=stat.outcome_magnitude_cv,
                direction_alignment_dispersion=stat.direction_alignment_dispersion,
                high_deviation_scenario_count=high,
                moderate_deviation_scenario_count=moderate,
                low_deviation_scenario_count=low,
                dominant_deviation_class=dominant,
                dispersion_driver_class=driver,
                profile_dispersion_class=dispersion,
                profile_research_readiness_class=readiness,
                profile_dispersion_diagnostic=profile_diagnostic(readiness),
                recommended_follow_up=profile_follow_up(readiness),
            )
        )
    return diagnostics


def _count_deviation(rows: list[ScenarioComparisonInput], deviation_class: str) -> int:
    return sum(1 for row in rows if row.scenario_deviation_class == deviation_class)
