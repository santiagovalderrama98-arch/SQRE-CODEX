"""Summary findings for Research Reference Store Design."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.models import ResearchReferenceStoreDesignSummary


def build_summary(
    candidates: pd.DataFrame,
    reference_store: pd.DataFrame,
    exclusion_review: pd.DataFrame,
    granularity_review: pd.DataFrame,
    horizon_review: pd.DataFrame,
    config: ResearchReferenceStoreDesignConfig,
) -> ResearchReferenceStoreDesignSummary:
    candidate_count = len(candidates)
    included_count = len(reference_store)
    core_count = _count(candidates, "Reference_Tier", "CORE_RESEARCH_REFERENCE")
    supporting_count = _count(candidates, "Reference_Tier", "SUPPORTING_RESEARCH_REFERENCE")
    watchlist_count = _count(candidates, "Reference_Tier", "WATCHLIST_RESEARCH_REFERENCE")
    excluded_count = max(0, candidate_count - included_count - watchlist_count)
    sample_count = _count(candidates, "Reference_Tier", "EXCLUDED_SAMPLE_CONSTRAINED")
    dispersion_count = _count(candidates, "Reference_Tier", "EXCLUDED_HIGH_DISPERSION")
    low_count = _count(candidates, "Reference_Tier", "EXCLUDED_LOW_INTERPRETABILITY")
    primary_granularity = _primary_value(
        granularity_review,
        "Context_Granularity",
        "Granularity_Reference_Utility_Class",
        "PRIMARY_REFERENCE_GRANULARITY",
    )
    primary_horizon = _primary_value(
        horizon_review,
        "Forward_Horizon_H4_Candles",
        "Horizon_Reference_Utility_Class",
        "PRIMARY_REFERENCE_HORIZON",
    )
    readiness_class, readiness_flag, follow_up = _readiness(
        candidate_count,
        included_count,
        core_count,
        sample_count,
        dispersion_count,
        low_count,
    )
    return ResearchReferenceStoreDesignSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        outcome_profile_count=candidate_count,
        reference_candidate_count=candidate_count,
        included_reference_count=included_count,
        core_reference_count=core_count,
        supporting_reference_count=supporting_count,
        watchlist_reference_count=watchlist_count,
        excluded_reference_count=excluded_count,
        excluded_sample_constrained_count=sample_count,
        excluded_high_dispersion_count=dispersion_count,
        excluded_low_interpretability_count=low_count,
        primary_reference_granularity=primary_granularity,
        primary_reference_horizon=primary_horizon,
        research_reference_store_readiness_class=readiness_class,
        research_reference_store_readiness_flag=readiness_flag,
        research_reference_store_diagnostic=_diagnostic(readiness_class),
        recommended_follow_up=follow_up,
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Research reference store usage review",
        "Expanded H4 historical data coverage",
        "Multi-pair replication",
        "Forex-calendar-adjusted continuity review",
        "Reference stability validation",
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
        "Findings depend on local H4/D1 forward outcome interpretation outputs.",
        "The H4 source sample may be partial due to provider row limits.",
        "Research references do not imply predictive edge.",
        "Research references are descriptive only.",
        "No operational decision is produced.",
    ]


def _readiness(
    candidate_count: int,
    included_count: int,
    core_count: int,
    sample_count: int,
    dispersion_count: int,
    low_count: int,
) -> tuple[str, str, str]:
    if candidate_count == 0:
        return "INPUT_MISSING", "INPUT_COMPLETENESS_REVIEW_REQUIRED", "REVIEW_INPUT_COMPLETENESS"
    if core_count > 0:
        return (
            "RESEARCH_REFERENCE_STORE_READY",
            "READY_FOR_RESEARCH_REFERENCE_STORE_USAGE_REVIEW",
            "RESEARCH_REFERENCE_STORE_USAGE_REVIEW",
        )
    if included_count > 0:
        return (
            "PARTIAL_RESEARCH_REFERENCE_STORE_READY",
            "PARTIAL_READY_FOR_RESEARCH_REFERENCE_STORE_USAGE_REVIEW",
            "REFERENCE_STABILITY_VALIDATION",
        )
    if sample_count >= max(dispersion_count, low_count):
        return (
            "RESEARCH_REFERENCE_STORE_SAMPLE_CONSTRAINED",
            "NOT_READY_REFERENCE_STORE_SAMPLE_CONSTRAINED",
            "EXPANDED_H4_HISTORICAL_DATA_COVERAGE",
        )
    return (
        "RESEARCH_REFERENCE_STORE_INPUT_LIMITED",
        "NOT_READY_REFERENCE_STORE_INPUT_LIMITED",
        "REVIEW_INPUT_COMPLETENESS",
    )


def _diagnostic(readiness_class: str) -> str:
    diagnostics = {
        "RESEARCH_REFERENCE_STORE_READY": "Reference store has core research references available for later research review.",
        "PARTIAL_RESEARCH_REFERENCE_STORE_READY": "Reference store has supporting references but limited core depth.",
        "RESEARCH_REFERENCE_STORE_SAMPLE_CONSTRAINED": "Reference store is constrained by historical sample depth.",
        "RESEARCH_REFERENCE_STORE_INPUT_LIMITED": "Reference store has limited included references due to input quality constraints.",
        "INPUT_MISSING": "Required interpretation inputs are missing or empty.",
    }
    return diagnostics[readiness_class]


def _count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column] == value).sum())


def _primary_value(frame: pd.DataFrame, value_column: str, class_column: str, target_class: str) -> str:
    if frame.empty or value_column not in frame.columns or class_column not in frame.columns:
        return "INPUT_MISSING"
    matches = frame[frame[class_column] == target_class]
    if not matches.empty:
        return str(matches.iloc[0][value_column])
    return str(frame.iloc[0][value_column])
