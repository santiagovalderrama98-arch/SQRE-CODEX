"""Findings and readiness classification for aligned forward outcome research."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.models import H4D1AlignedForwardOutcomeSummary


def build_summary(
    transition_alignment: pd.DataFrame,
    forward_outcomes: pd.DataFrame,
    outcome_profiles: pd.DataFrame,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> H4D1AlignedForwardOutcomeSummary:
    if transition_alignment.empty or forward_outcomes.empty:
        return H4D1AlignedForwardOutcomeSummary(
            config.symbol,
            config.h4_timeframe,
            config.d1_timeframe,
            len(transition_alignment),
            len(forward_outcomes),
            0,
            0,
            0,
            len(outcome_profiles),
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            "INPUT_MISSING",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "Aligned transition or H4 OHLC input is missing.",
            "REVIEW_INPUT_COMPLETENESS",
        )
    completeness = Counter(forward_outcomes["Outcome_Completeness_Class"])
    adequacy = Counter(outcome_profiles["Outcome_Sample_Adequacy_Class"]) if not outcome_profiles.empty else Counter()
    granularity = Counter(outcome_profiles["Context_Granularity"]) if not outcome_profiles.empty else Counter()
    ready = adequacy["OUTCOME_RESEARCH_READY_SAMPLE"]
    moderate = adequacy["MODERATE_OUTCOME_SAMPLE"]
    low_or_insufficient = adequacy["LOW_OUTCOME_SAMPLE"] + adequacy["INSUFFICIENT_OUTCOME_SAMPLE"]
    dominant = adequacy.most_common(1)[0][0] if adequacy else "INPUT_MISSING"
    readiness, diagnostic, follow_up = classify_readiness(ready, moderate, low_or_insufficient, len(outcome_profiles))
    return H4D1AlignedForwardOutcomeSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        aligned_h4_transition_row_count=len(transition_alignment),
        forward_outcome_row_count=len(forward_outcomes),
        complete_forward_outcome_row_count=completeness["COMPLETE_FORWARD_WINDOW"],
        partial_forward_outcome_row_count=completeness["PARTIAL_FORWARD_WINDOW"],
        missing_forward_outcome_row_count=completeness["MISSING_FORWARD_WINDOW"],
        outcome_profile_count=len(outcome_profiles),
        research_ready_outcome_profile_count=ready,
        moderate_outcome_profile_count=moderate,
        low_or_insufficient_outcome_profile_count=low_or_insufficient,
        h4_transition_only_profile_count=granularity["H4_TRANSITION_ONLY"],
        h4_transition_d1_market_state_profile_count=granularity["H4_TRANSITION_PLUS_D1_MARKET_STATE"],
        h4_transition_d1_regime_profile_count=granularity["H4_TRANSITION_PLUS_D1_REGIME"],
        h4_transition_d1_state_regime_profile_count=granularity["H4_TRANSITION_PLUS_D1_STATE_AND_REGIME"],
        dominant_outcome_readiness_class=dominant,
        h4_d1_aligned_forward_outcome_readiness_flag=readiness,
        h4_d1_aligned_forward_outcome_diagnostic=diagnostic,
        recommended_follow_up=follow_up,
    )


def classify_readiness(
    ready_count: int,
    moderate_count: int,
    low_or_insufficient_count: int,
    profile_count: int,
) -> tuple[str, str, str]:
    if profile_count <= 0:
        return (
            "NOT_READY_OUTCOME_INPUT_LIMITED",
            "No forward outcome profiles were produced.",
            "REVIEW_INPUT_COMPLETENESS",
        )
    if ready_count > 0 and low_or_insufficient_count == 0:
        return (
            "READY_FOR_H4_D1_OUTCOME_INTERPRETATION_REVIEW",
            "Forward outcome profiles are research-ready for later interpretation review.",
            "OUTCOME_INTERPRETATION_REVIEW",
        )
    if ready_count > 0 or moderate_count > 0:
        return (
            "PARTIAL_READY_FOR_H4_D1_OUTCOME_INTERPRETATION_REVIEW",
            "Some forward outcome profiles have usable descriptive sample depth.",
            "OUTCOME_INTERPRETATION_REVIEW",
        )
    return (
        "NOT_READY_OUTCOME_SAMPLE_CONSTRAINED",
        "Forward outcome profiles are sample-constrained.",
        "EXPANDED_H4_HISTORICAL_DATA_COVERAGE",
    )


def readiness_lines(summary: H4D1AlignedForwardOutcomeSummary | None) -> list[str]:
    if summary is None:
        return ["No readiness summary was produced."]
    return [
        f"Dominant outcome readiness class: {summary.dominant_outcome_readiness_class}",
        f"H4/D1 aligned forward outcome readiness flag: {summary.h4_d1_aligned_forward_outcome_readiness_flag}",
        f"Diagnostic: {summary.h4_d1_aligned_forward_outcome_diagnostic}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "Outcome interpretation review",
        "Expanded H4 historical data coverage",
        "Forex-calendar-adjusted continuity review",
        "Multi-pair replication",
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
        "No trading interpretation was produced.",
        "No signals were produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local same-time alignment outputs and H4 OHLC data.",
        "The H4 source sample may be partial due to provider row limits.",
        "Forward outcome statistics do not imply predictive edge.",
        "Directional outcome ratios are descriptive only.",
        "No operational decision is produced.",
    ]
