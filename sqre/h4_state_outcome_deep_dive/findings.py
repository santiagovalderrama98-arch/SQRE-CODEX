"""Descriptive findings for H4 state outcome deep dive."""

from __future__ import annotations

from sqre.h4_state_outcome_deep_dive.config import H4StateOutcomeDeepDiveConfig


def stability_class(forward_range_cv: float, outcome_magnitude_cv: float, config: H4StateOutcomeDeepDiveConfig) -> str:
    if forward_range_cv >= config.high_dispersion_threshold or outcome_magnitude_cv >= config.high_dispersion_threshold:
        return "HIGH_DISPERSION"
    if (
        forward_range_cv >= config.moderate_dispersion_threshold
        or outcome_magnitude_cv >= config.moderate_dispersion_threshold
    ):
        return "MODERATE_DISPERSION"
    return "STABLE_DESCRIPTIVE"


def scenario_observation_diagnostic(profile_type: str, sample_size: int, config: H4StateOutcomeDeepDiveConfig) -> str:
    if sample_size < config.minimum_total_sample_size:
        return "Scenario observation has limited sample size"
    if profile_type == "SCENARIO_SENSITIVE_OBSERVATION":
        return "Scenario observation belongs to a scenario-sensitive H4 state profile"
    if profile_type == "SAMPLE_CONSTRAINED_OBSERVATION":
        return "Scenario observation belongs to a sample-constrained H4 state profile"
    return "Scenario observation supports descriptive H4 state outcome review"


def outcome_profile_diagnostic(profile_type: str, stability: str) -> str:
    if profile_type == "SCENARIO_SENSITIVE_OBSERVATION":
        return "H4 state outcome profile requires scenario-sensitive interpretation"
    if profile_type == "SAMPLE_CONSTRAINED_OBSERVATION":
        return "H4 state outcome profile requires sample adequacy review"
    if profile_type == "RESEARCH_READY" and stability == "STABLE_DESCRIPTIVE":
        return "H4 state outcome profile is suitable for deeper descriptive review"
    if profile_type == "RESEARCH_READY" and stability == "MODERATE_DISPERSION":
        return "H4 state outcome profile is suitable for deeper descriptive review with dispersion monitoring"
    if stability == "HIGH_DISPERSION":
        return "H4 state outcome profile requires dispersion review before aggregation"
    return "H4 state outcome profile requires further descriptive review"


def outcome_profile_follow_up(stability: str, profile_type: str) -> str:
    if profile_type == "SAMPLE_CONSTRAINED_OBSERVATION":
        return "Review sample adequacy before broader aggregation."
    if profile_type == "SCENARIO_SENSITIVE_OBSERVATION":
        return "Review scenario-sensitive H4 state profile separately."
    if stability == "HIGH_DISPERSION":
        return "Review dispersion before broader aggregation."
    if stability == "MODERATE_DISPERSION":
        return "Continue descriptive review with dispersion monitoring."
    return "Continue descriptive H4 state outcome review."


def scenario_deviation_class(mean_normalized_deviation: float, config: H4StateOutcomeDeepDiveConfig) -> str:
    if mean_normalized_deviation >= config.high_dispersion_threshold:
        return "HIGH_DEVIATION"
    if mean_normalized_deviation >= config.moderate_dispersion_threshold:
        return "MODERATE_DEVIATION"
    return "LOW_DEVIATION"


def scenario_comparison_diagnostic(deviation_class: str) -> str:
    if deviation_class == "HIGH_DEVIATION":
        return "Scenario-period observation differs materially from the selected profile average"
    if deviation_class == "MODERATE_DEVIATION":
        return "Scenario-period observation differs moderately from the selected profile average"
    return "Scenario-period observation remains near the selected profile average"


def state_summary_diagnostic(ready_count: int, sample_count: int, scenario_count: int, high_count: int) -> str:
    if high_count:
        return "H4 state label includes profiles requiring dispersion review"
    if scenario_count:
        return "H4 state label includes scenario-sensitive observation profiles"
    if sample_count:
        return "H4 state label includes sample-constrained observation profiles"
    if ready_count:
        return "H4 state label contains research-ready descriptive profiles"
    return "H4 state label requires further descriptive review"


def state_summary_follow_up(sample_count: int, scenario_count: int, high_count: int) -> str:
    if high_count:
        return "Review high-dispersion profiles before broader aggregation."
    if scenario_count:
        return "Review scenario-sensitive observations separately."
    if sample_count:
        return "Review sample adequacy before broader aggregation."
    return "Continue descriptive H4 state outcome review."
