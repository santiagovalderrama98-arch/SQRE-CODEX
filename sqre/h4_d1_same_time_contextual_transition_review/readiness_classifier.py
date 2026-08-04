"""Readiness classification for H4/D1 same-time contextual transition review."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.models import ContextualTransitionSummary


def build_summary(
    profiles: pd.DataFrame,
    concentration_review: pd.DataFrame,
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> ContextualTransitionSummary:
    if profiles.empty:
        return ContextualTransitionSummary(
            config.symbol,
            config.h4_timeframe,
            config.d1_timeframe,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            "SAME_TIME_CONTEXT_INPUT_LIMITED",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "Same-time contextual transition input is missing or empty.",
            "REVIEW_SAME_TIME_ALIGNMENT_INPUT_COMPLETENESS",
        )

    sample_counts = Counter(profiles["Context_Sample_Adequacy_Class"])
    review_counts = Counter(profiles["Contextual_Review_Class"])
    distribution_counts = Counter(
        concentration_review.get("Transition_Context_Distribution_Class", pd.Series(dtype=str))
    )
    dominant_review_class = review_counts.most_common(1)[0][0]
    readiness_flag, diagnostic, follow_up = _readiness(sample_counts, dominant_review_class)
    return ContextualTransitionSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        aligned_h4_transition_row_count=int(profiles["Context_Row_Count"].sum()),
        distinct_h4_transition_count=int(profiles["H4_Transition_Label"].nunique()),
        distinct_d1_market_state_count=int(profiles["D1_Market_State"].nunique()),
        distinct_d1_regime_count=int(profiles["D1_Regime_Label"].nunique()),
        context_profile_count=len(profiles),
        research_ready_context_count=sample_counts["RESEARCH_READY_CONTEXT_SAMPLE"],
        moderate_context_count=sample_counts["MODERATE_CONTEXT_SAMPLE"],
        low_sample_context_count=sample_counts["LOW_CONTEXT_SAMPLE"],
        insufficient_context_count=sample_counts["INSUFFICIENT_CONTEXT_SAMPLE"],
        d1_context_concentrated_transition_count=distribution_counts["D1_CONTEXT_CONCENTRATED"],
        d1_context_mixed_transition_count=distribution_counts["D1_CONTEXT_MIXED"],
        d1_context_dispersed_transition_count=distribution_counts["D1_CONTEXT_DISPERSED"],
        dominant_contextual_review_class=dominant_review_class,
        h4_d1_contextual_transition_readiness_flag=readiness_flag,
        h4_d1_contextual_transition_diagnostic=diagnostic,
        recommended_follow_up=follow_up,
    )


def _readiness(sample_counts: Counter, dominant_review_class: str) -> tuple[str, str, str]:
    ready = sample_counts["RESEARCH_READY_CONTEXT_SAMPLE"]
    moderate = sample_counts["MODERATE_CONTEXT_SAMPLE"]
    constrained = sample_counts["LOW_CONTEXT_SAMPLE"] + sample_counts["INSUFFICIENT_CONTEXT_SAMPLE"]
    if ready > 0 and ready >= constrained:
        return (
            "READY_FOR_H4_D1_ALIGNED_OUTCOME_RESEARCH",
            "Same-time contextual transition profiles include research-ready samples.",
            "H4_D1_ALIGNED_FORWARD_OUTCOME_RESEARCH",
        )
    if ready > 0 or moderate > 0:
        return (
            "PARTIAL_READY_FOR_H4_D1_ALIGNED_OUTCOME_RESEARCH",
            "Some same-time contextual transition profiles are usable, while others remain sample-constrained.",
            "D1_REGIME_CONTEXT_ADEQUACY_REVIEW",
        )
    if dominant_review_class == "SAME_TIME_CONTEXT_SAMPLE_CONSTRAINED":
        return (
            "NOT_READY_CONTEXT_SAMPLE_CONSTRAINED",
            "Same-time contextual transition profiles are dominated by constrained samples.",
            "EXPANDED_H4_HISTORICAL_DATA_COVERAGE",
        )
    return (
        "NOT_READY_CONTEXT_INPUT_LIMITED",
        "Same-time contextual transition profile coverage is input-limited.",
        "REVIEW_SAME_TIME_ALIGNMENT_INPUT_COMPLETENESS",
    )
