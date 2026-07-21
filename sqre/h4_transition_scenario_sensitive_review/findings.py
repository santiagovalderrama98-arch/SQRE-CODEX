"""Descriptive findings for H4 transition scenario-sensitive review."""

from __future__ import annotations


def profile_diagnostic(sensitivity_class: str) -> str:
    return {
        "HIGH_TRANSITION_SCENARIO_SENSITIVITY": "H4 transition profile requires scenario-sensitive interpretation",
        "MODERATE_TRANSITION_SCENARIO_SENSITIVITY": "H4 transition profile shows moderate scenario sensitivity",
        "LOW_TRANSITION_SCENARIO_SENSITIVITY": "H4 transition profile shows limited scenario deviation",
    }.get(sensitivity_class, "H4 transition profile requires scenario-sensitive interpretation")


def profile_follow_up(sensitivity_class: str, near_candidate_flag: str) -> str:
    if near_candidate_flag == "YES":
        return "H4 transition profile may be revisited for later selective aggregation review."
    if sensitivity_class == "HIGH_TRANSITION_SCENARIO_SENSITIVITY":
        return "Review scenario-period deviation before aggregation review."
    return "Continue descriptive scenario-sensitive transition review."


def scenario_deviation_diagnostic(intensity_class: str) -> str:
    return {
        "HIGH": "Scenario-period row shows elevated transition deviation",
        "MODERATE": "Scenario-period row shows moderate transition deviation",
        "LOW": "Scenario-period row shows limited transition deviation",
    }.get(intensity_class, "Scenario-period row requires descriptive review")


def scenario_review_diagnostic(recurrent_class: str) -> str:
    return {
        "HIGH_RECURRENT_DEVIATION": "Scenario-period repeatedly contributes elevated deviation",
        "MODERATE_RECURRENT_DEVIATION": "Scenario-period contributes moderate recurrent deviation",
        "LOW_RECURRENT_DEVIATION": "Scenario-period contributes limited recurrent deviation",
    }.get(recurrent_class, "Scenario-period requires descriptive review")


def transition_family_diagnostic(high_count: int, near_count: int, profile_count: int) -> str:
    if profile_count and high_count > profile_count / 2:
        return "H4 transition family remains scenario-sensitive across forward windows"
    if near_count > 0:
        return "H4 transition family contains profiles that may be revisited for selective aggregation review"
    return "H4 transition family requires further scenario-sensitive review"


def state_sensitivity_diagnostic(high_count: int, near_count: int, profile_count: int) -> str:
    if profile_count and high_count > profile_count / 2:
        return "Transition profiles connected to this state remain scenario-sensitive"
    if near_count > 0:
        return "Transition profiles connected to this state contain profiles that may be revisited for selective aggregation review"
    return "Transition profiles connected to this state require further scenario-sensitive review"


def window_sensitivity_diagnostic(high_count: int, near_count: int, profile_count: int) -> str:
    if profile_count and high_count > profile_count / 2:
        return "Forward window remains scenario-sensitive across H4 transition profiles"
    if near_count > 0:
        return "Forward window contains profiles that may be revisited for selective aggregation review"
    return "Forward window requires further scenario-sensitive review"


def group_follow_up(high_count: int, near_count: int, total_count: int) -> str:
    if near_count > 0:
        return "Review near-candidate transition profiles separately."
    if total_count and high_count > total_count / 2:
        return "Continue scenario-sensitive interpretation."
    return "Continue descriptive transition review."


def summary_diagnostic(near_candidate_count: int, high_sensitivity_count: int, reviewed_count: int) -> str:
    if near_candidate_count > 0:
        return "H4 transition profiles contain a limited subset that may be revisited for later selective aggregation review"
    if reviewed_count and high_sensitivity_count > reviewed_count / 2:
        return "H4 transition profiles remain scenario-sensitive and require scenario-level interpretation"
    return "H4 transition scenario-sensitive review requires further descriptive analysis"


def summary_follow_up(near_candidate_count: int, high_sensitivity_count: int, reviewed_count: int) -> str:
    if near_candidate_count > 0:
        return "Review near-candidate transition profiles separately before later aggregation study."
    if reviewed_count and high_sensitivity_count > reviewed_count / 2:
        return "Continue scenario-sensitive interpretation of H4 transition profiles."
    return "Continue descriptive H4 transition scenario-sensitive review."
