"""Descriptive findings for H4 scenario-sensitive state review."""

from __future__ import annotations


def profile_diagnostic(sensitivity_class: str) -> str:
    return {
        "HIGH_SCENARIO_SENSITIVITY": "H4 state profile requires scenario-sensitive interpretation",
        "MODERATE_SCENARIO_SENSITIVITY": "H4 state profile shows moderate scenario sensitivity",
        "LOW_SCENARIO_SENSITIVITY": "H4 state profile shows limited scenario deviation",
    }.get(sensitivity_class, "H4 state profile requires scenario-sensitive interpretation")


def profile_follow_up(sensitivity_class: str, near_candidate_flag: str) -> str:
    if near_candidate_flag == "YES":
        return "H4 state profile may be revisited for later selective aggregation review."
    if sensitivity_class == "HIGH_SCENARIO_SENSITIVITY":
        return "Review scenario-period deviation before aggregation review."
    return "Continue descriptive scenario-sensitive state review."


def scenario_deviation_diagnostic(intensity_class: str) -> str:
    return {
        "HIGH": "Scenario-period row shows elevated deviation",
        "MODERATE": "Scenario-period row shows moderate deviation",
        "LOW": "Scenario-period row shows limited deviation",
    }.get(intensity_class, "Scenario-period row requires descriptive review")


def scenario_review_diagnostic(recurrent_class: str) -> str:
    return {
        "HIGH_RECURRENT_DEVIATION": "Scenario-period repeatedly contributes elevated deviation",
        "MODERATE_RECURRENT_DEVIATION": "Scenario-period contributes moderate recurrent deviation",
        "LOW_RECURRENT_DEVIATION": "Scenario-period contributes limited recurrent deviation",
    }.get(recurrent_class, "Scenario-period requires descriptive review")


def state_sensitivity_diagnostic(high_count: int, near_count: int, profile_count: int) -> str:
    if profile_count and high_count > profile_count / 2:
        return "H4 state label remains scenario-sensitive across forward windows"
    if near_count > 0:
        return "H4 state label contains profiles that may be revisited for selective aggregation review"
    return "H4 state label requires further scenario-sensitive review"


def window_sensitivity_diagnostic(high_count: int, near_count: int, profile_count: int) -> str:
    if profile_count and high_count > profile_count / 2:
        return "Forward window remains scenario-sensitive across H4 state profiles"
    if near_count > 0:
        return "Forward window contains profiles that may be revisited for selective aggregation review"
    return "Forward window requires further scenario-sensitive review"


def summary_diagnostic(near_candidate_count: int, high_sensitivity_count: int, reviewed_count: int) -> str:
    if near_candidate_count > 0:
        return "H4 contains a limited subset that may be revisited for later selective aggregation review"
    if reviewed_count and high_sensitivity_count > reviewed_count / 2:
        return "H4 state profiles remain scenario-sensitive and require scenario-level interpretation"
    return "H4 scenario-sensitive review requires further descriptive analysis"


def summary_follow_up(near_candidate_count: int, high_sensitivity_count: int, reviewed_count: int) -> str:
    if near_candidate_count > 0:
        return "Review near-candidate profiles separately before later aggregation study."
    if reviewed_count and high_sensitivity_count > reviewed_count / 2:
        return "Continue scenario-sensitive interpretation of H4 state profiles."
    return "Continue descriptive H4 scenario-sensitive state review."
