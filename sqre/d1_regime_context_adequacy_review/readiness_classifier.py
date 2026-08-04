"""Readiness classification for D1 regime context adequacy review."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.models import D1RegimeContextAdequacySummary


def build_summary(
    profiles: pd.DataFrame,
    d1_context_inventory: pd.DataFrame,
    fragmentation_review: pd.DataFrame,
    sample_loss_review: pd.DataFrame,
    aggregation_candidate_review: pd.DataFrame,
    config: D1RegimeContextAdequacyReviewConfig,
) -> D1RegimeContextAdequacySummary:
    if profiles.empty:
        return D1RegimeContextAdequacySummary(
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
            0,
            "D1_CONTEXT_INPUT_LIMITED",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "D1 context adequacy input is missing or empty.",
            "REVIEW_CONTEXTUAL_TRANSITION_INPUT_COMPLETENESS",
        )

    sample_counts = Counter(profiles["Context_Sample_Adequacy_Class"])
    adequacy_counts = Counter(d1_context_inventory.get("D1_Context_Adequacy_Class", pd.Series(dtype=str)))
    dominant_adequacy = adequacy_counts.most_common(1)[0][0] if adequacy_counts else "D1_CONTEXT_INPUT_LIMITED"
    high_fragmentation = int((fragmentation_review["D1_Fragmentation_Class"] == "HIGH_D1_CONTEXT_FRAGMENTATION").sum())
    extreme_fragmentation = int(
        (fragmentation_review["D1_Fragmentation_Class"] == "EXTREME_D1_CONTEXT_FRAGMENTATION").sum()
    )
    high_sample_loss = int((sample_loss_review["Transition_Sample_Loss_Class"] == "HIGH_SAMPLE_LOSS").sum())
    extreme_sample_loss = int((sample_loss_review["Transition_Sample_Loss_Class"] == "EXTREME_SAMPLE_LOSS").sum())
    candidate_count = int(
        aggregation_candidate_review[
            aggregation_candidate_review["Aggregation_Candidate_Class"].ne("INPUT_LIMITED")
        ].shape[0]
    ) if not aggregation_candidate_review.empty else 0
    readiness, diagnostic, follow_up = classify_readiness(
        research_ready_count=sample_counts["RESEARCH_READY_CONTEXT_SAMPLE"],
        low_or_insufficient_count=sample_counts["LOW_CONTEXT_SAMPLE"] + sample_counts["INSUFFICIENT_CONTEXT_SAMPLE"],
        high_fragmentation_count=high_fragmentation,
        extreme_fragmentation_count=extreme_fragmentation,
        high_sample_loss_count=high_sample_loss,
        extreme_sample_loss_count=extreme_sample_loss,
        aggregation_candidate_count=candidate_count,
    )
    return D1RegimeContextAdequacySummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        aligned_h4_transition_row_count=int(profiles["Context_Row_Count"].sum()),
        distinct_h4_transition_count=int(profiles["H4_Transition_Label"].nunique()),
        distinct_d1_market_state_count=int(profiles["D1_Market_State"].nunique()),
        distinct_d1_regime_count=int(profiles["D1_Regime_Label"].nunique()),
        context_profile_count=len(profiles),
        research_ready_context_count=sample_counts["RESEARCH_READY_CONTEXT_SAMPLE"],
        low_or_insufficient_context_count=sample_counts["LOW_CONTEXT_SAMPLE"] + sample_counts["INSUFFICIENT_CONTEXT_SAMPLE"],
        d1_context_count=len(d1_context_inventory),
        high_fragmentation_transition_count=high_fragmentation,
        extreme_fragmentation_transition_count=extreme_fragmentation,
        high_sample_loss_transition_count=high_sample_loss,
        extreme_sample_loss_transition_count=extreme_sample_loss,
        aggregation_candidate_count=candidate_count,
        dominant_d1_context_adequacy_class=dominant_adequacy,
        d1_regime_context_adequacy_readiness_flag=readiness,
        d1_regime_context_adequacy_diagnostic=diagnostic,
        recommended_follow_up=follow_up,
    )


def classify_readiness(
    *,
    research_ready_count: int,
    low_or_insufficient_count: int,
    high_fragmentation_count: int,
    extreme_fragmentation_count: int,
    high_sample_loss_count: int,
    extreme_sample_loss_count: int,
    aggregation_candidate_count: int,
) -> tuple[str, str, str]:
    if research_ready_count <= 0 and low_or_insufficient_count <= 0:
        return (
            "NOT_READY_INPUT_LIMITED",
            "D1 context adequacy review is input-limited.",
            "REVIEW_CONTEXTUAL_TRANSITION_INPUT_COMPLETENESS",
        )
    if extreme_fragmentation_count > 0:
        return (
            "NOT_READY_D1_CONTEXT_OVER_FRAGMENTED",
            "D1 context segmentation is dominated by extreme fragmentation.",
            "D1_REGIME_GROUPING_RESEARCH",
        )
    if high_fragmentation_count > 0 or aggregation_candidate_count > 0:
        return (
            "NOT_READY_D1_CONTEXT_SAMPLE_CONSTRAINED",
            "D1 context segmentation creates many constrained samples.",
            "D1_REGIME_GROUPING_RESEARCH",
        )
    if extreme_sample_loss_count > 0 or high_sample_loss_count > 0:
        return (
            "PARTIAL_READY_REQUIRES_D1_CONTEXT_FILTERING",
            "Some H4 transitions lose adequacy after D1 context segmentation.",
            "D1_CONTEXT_FILTERING_REVIEW",
        )
    if research_ready_count > 0:
        return (
            "READY_FOR_LIMITED_H4_D1_ALIGNED_OUTCOME_RESEARCH",
            "At least one D1 context profile is ready for limited later outcome research.",
            "LIMITED_H4_D1_ALIGNED_OUTCOME_RESEARCH",
        )
    return (
        "NOT_READY_D1_CONTEXT_SAMPLE_CONSTRAINED",
        "D1 context samples are constrained for later outcome research.",
        "EXPANDED_H4_HISTORICAL_DATA_COVERAGE",
    )
