"""Descriptive findings for D1 state outcome deep dive."""

from __future__ import annotations

from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig


def stability_class(forward_range_cv: float, outcome_magnitude_cv: float, config: D1StateOutcomeDeepDiveConfig) -> str:
    if forward_range_cv >= config.high_dispersion_threshold or outcome_magnitude_cv >= config.high_dispersion_threshold:
        return "HIGH_DISPERSION"
    if (
        forward_range_cv >= config.moderate_dispersion_threshold
        or outcome_magnitude_cv >= config.moderate_dispersion_threshold
    ):
        return "MODERATE_DISPERSION"
    return "STABLE_DESCRIPTIVE"


def regime_observation_diagnostic(profile_type: str, sample_size: int, config: D1StateOutcomeDeepDiveConfig) -> str:
    if sample_size < config.minimum_total_sample_size:
        return "Regime observation has limited sample size"
    if profile_type == "REGIME_SENSITIVE_OBSERVATION":
        return "Regime observation belongs to a regime-sensitive state profile"
    return "Regime observation supports descriptive state outcome review"


def outcome_profile_diagnostic(profile_type: str, stability: str) -> str:
    if profile_type == "REGIME_SENSITIVE_OBSERVATION":
        return "State outcome profile requires regime-sensitive interpretation"
    if profile_type == "RESEARCH_READY" and stability == "STABLE_DESCRIPTIVE":
        return "State outcome profile is suitable for deeper descriptive review"
    if profile_type == "RESEARCH_READY" and stability == "MODERATE_DISPERSION":
        return "State outcome profile is suitable for deeper descriptive review with dispersion monitoring"
    if stability == "HIGH_DISPERSION":
        return "State outcome profile requires dispersion review before aggregation"
    return "State outcome profile requires further descriptive review"


def outcome_profile_follow_up(stability: str, profile_type: str) -> str:
    if profile_type == "REGIME_SENSITIVE_OBSERVATION":
        return "Review regime-sensitive state profile separately."
    if stability == "HIGH_DISPERSION":
        return "Review dispersion before broader aggregation."
    if stability == "MODERATE_DISPERSION":
        return "Continue descriptive review with dispersion monitoring."
    return "Continue descriptive state outcome review."


def regime_deviation_class(mean_normalized_deviation: float, config: D1StateOutcomeDeepDiveConfig) -> str:
    if mean_normalized_deviation >= config.high_dispersion_threshold:
        return "HIGH_DEVIATION"
    if mean_normalized_deviation >= config.moderate_dispersion_threshold:
        return "MODERATE_DEVIATION"
    return "LOW_DEVIATION"


def regime_comparison_diagnostic(deviation_class: str) -> str:
    if deviation_class == "HIGH_DEVIATION":
        return "Regime-period observation differs materially from the selected profile average"
    if deviation_class == "MODERATE_DEVIATION":
        return "Regime-period observation differs moderately from the selected profile average"
    return "Regime-period observation remains near the selected profile average"


def state_summary_diagnostic(research_ready_count: int, sensitive_count: int, high_dispersion_count: int) -> str:
    if high_dispersion_count:
        return "State label includes profiles requiring dispersion review"
    if sensitive_count:
        return "State label includes regime-sensitive observation profiles"
    if research_ready_count:
        return "State label contains research-ready descriptive profiles"
    return "State label requires further descriptive review"


def state_summary_follow_up(sensitive_count: int, high_dispersion_count: int) -> str:
    if high_dispersion_count:
        return "Review high-dispersion profiles before broader aggregation."
    if sensitive_count:
        return "Review regime-sensitive observations separately."
    return "Continue descriptive state outcome review."
