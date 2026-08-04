"""Summary findings for H4/D1 forward outcome interpretation review."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.context_granularity_review import best_supported_granularity
from sqre.h4_d1_forward_outcome_interpretation_review.interpretation_readiness_classifier import classify_readiness
from sqre.h4_d1_forward_outcome_interpretation_review.models import H4D1ForwardOutcomeInterpretationSummary


def build_summary(
    interpretability_review: pd.DataFrame,
    directional_review: pd.DataFrame,
    horizon_review: pd.DataFrame,
    granularity_review: pd.DataFrame,
    config: H4D1ForwardOutcomeInterpretationReviewConfig,
) -> H4D1ForwardOutcomeInterpretationSummary:
    profile_count = len(interpretability_review)
    interpretable = _count(interpretability_review, "Outcome_Interpretability_Class", "INTERPRETABLE_OUTCOME_PROFILE")
    moderate = _count(
        interpretability_review,
        "Outcome_Interpretability_Class",
        "MODERATELY_INTERPRETABLE_OUTCOME_PROFILE",
    )
    low = _count(interpretability_review, "Outcome_Interpretability_Class", "LOW_INTERPRETABILITY_OUTCOME_PROFILE")
    sample = _count(
        interpretability_review,
        "Outcome_Interpretability_Class",
        "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED",
    )
    dispersion = _count(
        interpretability_review,
        "Outcome_Interpretability_Class",
        "NOT_INTERPRETABLE_HIGH_DISPERSION",
    )
    dominant, flag, diagnostic, follow_up = classify_readiness(profile_count, interpretable, moderate, sample, dispersion)
    return H4D1ForwardOutcomeInterpretationSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        outcome_profile_count=profile_count,
        interpretable_profile_count=interpretable,
        moderately_interpretable_profile_count=moderate,
        low_interpretability_profile_count=low,
        sample_constrained_profile_count=sample,
        high_dispersion_profile_count=dispersion,
        upward_dominance_profile_count=_count(
            directional_review,
            "Directional_Behavior_Class",
            "OBSERVED_UPWARD_FOLLOW_THROUGH_DOMINANCE",
        ),
        downward_dominance_profile_count=_count(
            directional_review,
            "Directional_Behavior_Class",
            "OBSERVED_DOWNWARD_FOLLOW_THROUGH_DOMINANCE",
        ),
        mixed_behavior_profile_count=_count(
            directional_review,
            "Directional_Behavior_Class",
            "OBSERVED_MIXED_DIRECTIONAL_BEHAVIOR",
        ),
        stable_horizon_context_count=_count(horizon_review, "Horizon_Stability_Class", "STABLE_ACROSS_HORIZONS"),
        unstable_horizon_context_count=_count(horizon_review, "Horizon_Stability_Class", "UNSTABLE_ACROSS_HORIZONS"),
        best_supported_context_granularity=best_supported_granularity(granularity_review),
        dominant_interpretation_readiness_class=dominant,
        h4_d1_forward_outcome_interpretation_readiness_flag=flag,
        h4_d1_forward_outcome_interpretation_diagnostic=diagnostic,
        recommended_follow_up=follow_up,
    )


def readiness_lines(summary: H4D1ForwardOutcomeInterpretationSummary | None) -> list[str]:
    if summary is None:
        return ["No readiness summary was produced."]
    return [
        f"Dominant interpretation readiness class: {summary.dominant_interpretation_readiness_class}",
        f"H4/D1 forward outcome interpretation readiness flag: "
        f"{summary.h4_d1_forward_outcome_interpretation_readiness_flag}",
        f"Diagnostic: {summary.h4_d1_forward_outcome_interpretation_diagnostic}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "Research reference-store design",
        "Expanded H4 historical data coverage",
        "Multi-pair replication",
        "Forex-calendar-adjusted continuity review",
        "Outcome interpretation stability review",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No provider behavior was changed.",
        "No trading signals were produced.",
        "No operational recommendations were produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local H4/D1 forward outcome profiles.",
        "The H4 source sample may be partial due to provider row limits.",
        "Descriptive outcome interpretation does not imply predictive edge.",
        "Directional dominance is historical and descriptive only.",
        "No operational decision is produced.",
    ]


def _count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame:
        return 0
    return int((frame[column] == value).sum())
