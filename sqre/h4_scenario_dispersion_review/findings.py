"""Descriptive findings for H4 scenario dispersion review."""

from __future__ import annotations


def profile_diagnostic(readiness_class: str) -> str:
    return {
        "AGGREGATION_CANDIDATE": "H4 state profile may proceed to later descriptive aggregation review",
        "SCENARIO_SENSITIVE_REVIEW": "H4 state profile requires scenario-sensitive interpretation before aggregation",
        "SAMPLE_REVIEW": "H4 state profile requires sample adequacy review",
        "GENERAL_REVIEW": "H4 state profile requires further descriptive review",
    }.get(readiness_class, "H4 state profile requires further descriptive review")


def profile_follow_up(readiness_class: str) -> str:
    return {
        "AGGREGATION_CANDIDATE": "Continue with later descriptive aggregation review.",
        "SCENARIO_SENSITIVE_REVIEW": "Review scenario-period dispersion before aggregation.",
        "SAMPLE_REVIEW": "Review sample adequacy before broader aggregation.",
        "GENERAL_REVIEW": "Continue descriptive scenario dispersion review.",
    }.get(readiness_class, "Continue descriptive scenario dispersion review.")


def state_diagnostic(profile_count: int, aggregation_count: int, scenario_count: int, sample_count: int) -> str:
    if profile_count and scenario_count > profile_count / 2:
        return "H4 state label is primarily scenario-sensitive"
    if profile_count and aggregation_count > profile_count / 2:
        return "H4 state label has profiles suitable for later descriptive aggregation review"
    if profile_count and sample_count > profile_count / 2:
        return "H4 state label remains sample-constrained"
    return "H4 state label requires further dispersion review"


def state_follow_up(scenario_count: int, sample_count: int) -> str:
    if scenario_count:
        return "Review scenario-sensitive profiles separately."
    if sample_count:
        return "Review sample-constrained profiles separately."
    return "Continue descriptive state-level dispersion review."


def window_diagnostic(profile_count: int, high_count: int, stable_count: int, moderate_count: int) -> str:
    if profile_count and high_count > profile_count / 2:
        return "Forward window shows elevated dispersion across H4 state profiles"
    if profile_count and stable_count + moderate_count > profile_count / 2:
        return "Forward window has profiles suitable for later descriptive aggregation review"
    return "Forward window requires further dispersion review"


def window_follow_up(high_count: int) -> str:
    if high_count:
        return "Review high-dispersion forward window profiles separately."
    return "Continue descriptive forward window review."


def scenario_diagnostic(contribution_class: str) -> str:
    return {
        "HIGH_CONTRIBUTION": "Scenario contributes elevated deviation across H4 state profiles",
        "MODERATE_CONTRIBUTION": "Scenario contributes moderate deviation across H4 state profiles",
        "LOW_CONTRIBUTION": "Scenario contributes limited deviation across H4 state profiles",
    }.get(contribution_class, "Scenario contribution requires further descriptive review")


def h4_summary_diagnostic(aggregation_count: int, scenario_count: int, sample_count: int) -> str:
    if aggregation_count:
        return "H4 has a selective subset for later descriptive aggregation review"
    if scenario_count > sample_count:
        return "H4 state outcomes require scenario-sensitive review before aggregation"
    if sample_count:
        return "H4 condition universe remains sample constrained"
    return "H4 scenario dispersion review requires further descriptive analysis"


def h4_summary_follow_up(scenario_count: int, sample_count: int) -> str:
    if scenario_count:
        return "Review scenario-sensitive H4 state profiles before broader aggregation."
    if sample_count:
        return "Review sample-constrained H4 state profiles separately."
    return "Continue descriptive H4 scenario dispersion review."
