"""D1 regime-normalized research findings."""

from __future__ import annotations

from collections import Counter

from sqre.d1_regime_normalized_research.models import (
    D1RegimeConditionProfile,
    D1RegimeResearchSummary,
    D1RegimeScenarioData,
)
from sqre.d1_regime_normalized_research.regime_sensitivity import mean


def build_d1_regime_summary(
    scenarios: list[D1RegimeScenarioData],
    profiles: list[D1RegimeConditionProfile],
    state_profiles: list[D1RegimeConditionProfile],
    transition_profiles: list[D1RegimeConditionProfile],
) -> D1RegimeResearchSummary:
    completed = [scenario for scenario in scenarios if scenario.inventory.status == "COMPLETED"]
    adequate = [profile for profile in profiles if profile.sample_adequacy_flag == "ADEQUATE"]
    low_sample = [profile for profile in profiles if profile.sample_adequacy_flag == "LOW_SAMPLE"]
    stable = [profile for profile in profiles if profile.regime_sensitivity_flag == "STABLE"]
    moderate = [profile for profile in profiles if profile.regime_sensitivity_flag == "MODERATE"]
    high = [profile for profile in profiles if profile.regime_sensitivity_flag == "HIGH"]
    readiness = (
        "READY_FOR_DEEP_RESEARCH"
        if len(completed) >= 4 and len(adequate) > len(low_sample)
        else "REQUIRES_SAMPLE_REVIEW"
    )
    sensitivity = "REGIME_SENSITIVE" if high else "MIXED"
    return D1RegimeResearchSummary(
        timeframe="D1",
        scenario_count=len(scenarios),
        regime_count=len({scenario.inventory.regime_id for scenario in scenarios}),
        completed_scenario_count=len(completed),
        total_ohlc_rows=sum(scenario.inventory.ohlc_rows for scenario in scenarios),
        average_structures_detected=mean([scenario.inventory.structures_detected for scenario in scenarios]),
        average_unique_states=mean([scenario.inventory.unique_states for scenario in scenarios]),
        most_common_state_mode=_mode([scenario.inventory.most_common_state for scenario in scenarios]),
        condition_profile_count=len(profiles),
        state_condition_profile_count=len(state_profiles),
        transition_condition_profile_count=len(transition_profiles),
        average_regime_count_per_profile=mean([profile.regime_count for profile in profiles]),
        adequate_profile_count=len(adequate),
        low_sample_profile_count=len(low_sample),
        stable_outcome_profile_count=len(stable),
        moderate_sensitivity_profile_count=len(moderate),
        high_sensitivity_profile_count=len(high),
        average_forward_range_cv=mean([profile.forward_range_cv for profile in profiles]),
        average_outcome_magnitude_cv=mean([profile.outcome_magnitude_cv for profile in profiles]),
        average_direction_alignment_rate=mean([profile.average_direction_alignment_rate for profile in profiles]),
        research_readiness_flag=readiness,
        regime_sensitivity_profile=sensitivity,
        recommended_follow_up=_summary_follow_up(high, stable, profiles),
    )


def summary_diagnostic(summary: D1RegimeResearchSummary | None) -> str:
    if summary is None:
        return "D1 regime-normalized research requires further review"
    if summary.high_sensitivity_profile_count > 0:
        return "D1 price outcomes require regime-normalized interpretation"
    if summary.condition_profile_count > 0 and summary.stable_outcome_profile_count >= summary.condition_profile_count / 2:
        return "D1 price outcomes appear relatively stable across available scenario regimes"
    return "D1 regime-normalized research requires further review"


def _summary_follow_up(
    high_profiles: list[D1RegimeConditionProfile],
    stable_profiles: list[D1RegimeConditionProfile],
    profiles: list[D1RegimeConditionProfile],
) -> str:
    if high_profiles:
        return "Review D1 regime-normalized outcome dispersion."
    if profiles and len(stable_profiles) >= len(profiles) / 2:
        return "Continue D1 stable profile review."
    return "Review D1 sample adequacy and regime coverage."


def _mode(values: list[str]) -> str:
    clean = [value for value in values if value]
    return Counter(clean).most_common(1)[0][0] if clean else ""
