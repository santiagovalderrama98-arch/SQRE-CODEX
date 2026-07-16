"""Select and classify H4 state profiles."""

from __future__ import annotations

from sqre.h4_state_outcome_deep_dive.config import H4StateOutcomeDeepDiveConfig
from sqre.h4_state_outcome_deep_dive.models import H4StateProfile, H4StateProfileInput


def select_h4_state_profiles(
    profiles: list[H4StateProfileInput],
    config: H4StateOutcomeDeepDiveConfig,
) -> list[H4StateProfile]:
    selected = [
        _classify(profile, config)
        for profile in profiles
        if profile.timeframe.strip().upper() == "H4" and profile.condition_type.strip().upper() == "STATE_CONDITION"
    ]
    if not config.include_sample_constrained_observations:
        selected = [profile for profile in selected if profile.profile_type != "SAMPLE_CONSTRAINED_OBSERVATION"]
    return sorted(selected, key=lambda item: (item.condition_label, item.forward_window, item.profile_type))


def dispersion_class(profile: H4StateProfileInput, config: H4StateOutcomeDeepDiveConfig) -> str:
    if profile.forward_range_cv >= config.high_dispersion_threshold or profile.outcome_magnitude_cv >= config.high_dispersion_threshold:
        return "HIGH_DISPERSION"
    if (
        profile.forward_range_cv >= config.moderate_dispersion_threshold
        or profile.outcome_magnitude_cv >= config.moderate_dispersion_threshold
    ):
        return "MODERATE_DISPERSION"
    return "STABLE_DESCRIPTIVE"


def _classify(profile: H4StateProfileInput, config: H4StateOutcomeDeepDiveConfig) -> H4StateProfile:
    dispersion = dispersion_class(profile, config)
    profile_type = _profile_type(profile, config)
    return H4StateProfile(
        condition_label=profile.condition_label,
        forward_window=profile.forward_window,
        profile_type=profile_type,
        scenario_count=profile.scenario_count,
        scenarios_present=profile.scenarios_present,
        total_sample_size=profile.total_sample_size,
        average_sample_size_per_scenario=profile.average_sample_size_per_scenario,
        average_forward_range_pips=profile.average_forward_range_pips,
        average_outcome_magnitude_pips=profile.average_outcome_magnitude_pips,
        average_direction_alignment_rate=profile.average_direction_alignment_rate,
        forward_range_cv=profile.forward_range_cv,
        outcome_magnitude_cv=profile.outcome_magnitude_cv,
        scenario_sensitivity_flag=profile.scenario_sensitivity_flag,
        sample_adequacy_flag=profile.sample_adequacy_flag,
        dispersion_class=dispersion,
        condition_research_class=_research_class(profile_type),
        profile_diagnostic=profile.outcome_profile_diagnostic,
        recommended_follow_up=_follow_up(profile_type, dispersion),
    )


def _profile_type(profile: H4StateProfileInput, config: H4StateOutcomeDeepDiveConfig) -> str:
    if profile.total_sample_size < config.minimum_total_sample_size or profile.scenario_count < config.minimum_scenario_count:
        return "SAMPLE_CONSTRAINED_OBSERVATION"
    if profile.forward_range_cv >= config.high_dispersion_threshold or profile.outcome_magnitude_cv >= config.high_dispersion_threshold:
        return "SCENARIO_SENSITIVE_OBSERVATION"
    return "RESEARCH_READY"


def _research_class(profile_type: str) -> str:
    return {
        "RESEARCH_READY": "RESEARCH_READY_DESCRIPTIVE",
        "SCENARIO_SENSITIVE_OBSERVATION": "SCENARIO_SENSITIVE_REVIEW",
        "SAMPLE_CONSTRAINED_OBSERVATION": "SAMPLE_REVIEW",
    }.get(profile_type, "SAMPLE_REVIEW")


def _follow_up(profile_type: str, dispersion: str) -> str:
    if profile_type == "SAMPLE_CONSTRAINED_OBSERVATION":
        return "Review sample adequacy before broader descriptive aggregation."
    if profile_type == "SCENARIO_SENSITIVE_OBSERVATION":
        return "Review scenario-sensitive state behavior separately."
    if dispersion == "MODERATE_DISPERSION":
        return "Continue descriptive review with dispersion monitoring."
    return "Continue descriptive H4 state outcome review."
