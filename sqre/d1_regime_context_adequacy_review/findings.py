"""Findings text for D1 regime context adequacy review."""

from __future__ import annotations

from sqre.d1_regime_context_adequacy_review.models import D1RegimeContextAdequacySummary


def readiness_lines(summary: D1RegimeContextAdequacySummary | None) -> list[str]:
    if summary is None:
        return ["No readiness summary was produced."]
    return [
        f"Dominant D1 context adequacy class: {summary.dominant_d1_context_adequacy_class}",
        f"D1 regime context adequacy readiness flag: {summary.d1_regime_context_adequacy_readiness_flag}",
        f"Diagnostic: {summary.d1_regime_context_adequacy_diagnostic}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "Expanded H4 historical data coverage",
        "Forex-calendar-adjusted continuity review",
        "Limited H4/D1 aligned outcome research on research-ready contexts",
        "D1 regime grouping research",
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
        "No D1 regime aggregation was applied.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local same-time contextual transition outputs.",
        "The H4 source sample may be partial due to provider row limits.",
        "D1 context adequacy does not imply predictive edge.",
        "Fragmentation and sample adequacy are descriptive only.",
        "No operational decision is produced.",
    ]
