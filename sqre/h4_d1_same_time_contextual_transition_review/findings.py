"""Findings text for H4/D1 same-time contextual transition review."""

from __future__ import annotations

from sqre.h4_d1_same_time_contextual_transition_review.models import ContextualTransitionSummary


def readiness_lines(summary: ContextualTransitionSummary | None) -> list[str]:
    if summary is None:
        return ["No readiness summary was produced."]
    return [
        f"Dominant contextual review class: {summary.dominant_contextual_review_class}",
        f"H4/D1 contextual transition readiness flag: {summary.h4_d1_contextual_transition_readiness_flag}",
        f"Diagnostic: {summary.h4_d1_contextual_transition_diagnostic}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4/D1 aligned forward outcome research",
        "D1 regime context adequacy review",
        "Expanded H4 historical data coverage",
        "Forex-calendar-adjusted continuity review",
        "Research reference-store design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No provider behavior was changed.",
        "No H4/D1 outcome research was produced.",
        "No trading interpretation was produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local same-time alignment outputs.",
        "The H4 source sample may be partial due to provider row limits.",
        "Context sample adequacy does not imply predictive edge.",
        "Frequency and concentration are descriptive only.",
        "No operational decision is produced.",
    ]
