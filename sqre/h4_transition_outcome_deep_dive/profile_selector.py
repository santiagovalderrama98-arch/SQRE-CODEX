"""Select and classify H4 transition profiles."""

from __future__ import annotations

from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.models import H4TransitionProfile, H4TransitionProfileInput
from sqre.h4_transition_outcome_deep_dive.transition_parser import parse_transition_label


def select_h4_transition_profiles(
    profiles: list[H4TransitionProfileInput],
    config: H4TransitionOutcomeDeepDiveConfig,
) -> list[H4TransitionProfile]:
    selected = [
        _classify(profile, config)
        for profile in profiles
        if profile.timeframe.strip().upper() == "H4" and profile.condition_type.strip().upper() == "TRANSITION_CONDITION"
    ]
    if not config.include_sample_constrained_observations:
        selected = [profile for profile in selected if profile.profile_type != "SAMPLE_CONSTRAINED_OBSERVATION"]
    return sorted(selected, key=lambda item: (item.condition_label, item.forward_window, item.profile_type))


def dispersion_class(profile: H4TransitionProfileInput, config: H4TransitionOutcomeDeepDiveConfig) -> str:
    if profile.forward_range_cv >= config.high_dispersion_threshold or profile.outcome_magnitude_cv >= config.high_dispersion_threshold:
        return "HIGH_DISPERSION"
    if (
        profile.forward_range_cv >= config.moderate_dispersion_threshold
        or profile.outcome_magnitude_cv >= config.moderate_dispersion_threshold
    ):
        return "MODERATE_DISPERSION"
    return "STABLE_DESCRIPTIVE"


def _classify(profile: H4TransitionProfileInput, config: H4TransitionOutcomeDeepDiveConfig) -> H4TransitionProfile:
    dispersion = dispersion_class(profile, config)
    profile_type = _profile_type(profile, config)
    parsed = parse_transition_label(profile.condition_label)
    return H4TransitionProfile(
        condition_label=profile.condition_label,
        source_state=parsed.source_state,
        target_state=parsed.target_state,
        transition_family=parsed.transition_family,
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
        transition_research_class=_research_class(profile_type),
        profile_diagnostic=profile.outcome_profile_diagnostic or _profile_diagnostic(profile_type, dispersion),
        recommended_follow_up=_follow_up(profile_type, dispersion),
    )


def _profile_type(profile: H4TransitionProfileInput, config: H4TransitionOutcomeDeepDiveConfig) -> str:
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
        return "Review scenario-sensitive H4 transition behavior separately."
    if dispersion == "MODERATE_DISPERSION":
        return "Continue descriptive review with dispersion monitoring."
    return "Continue descriptive H4 transition outcome review."


def _profile_diagnostic(profile_type: str, dispersion: str) -> str:
    if profile_type == "SCENARIO_SENSITIVE_OBSERVATION":
        return "H4 transition outcome profile requires scenario-sensitive interpretation"
    if profile_type == "SAMPLE_CONSTRAINED_OBSERVATION":
        return "H4 transition outcome profile requires sample adequacy review"
    if dispersion == "MODERATE_DISPERSION":
        return "H4 transition outcome profile is suitable for deeper descriptive review with dispersion monitoring"
    if dispersion == "HIGH_DISPERSION":
        return "H4 transition outcome profile requires dispersion review before aggregation"
    return "H4 transition outcome profile is suitable for deeper descriptive review"
