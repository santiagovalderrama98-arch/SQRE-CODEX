"""Readiness findings for Research Reference Store Usage Review."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.models import ResearchReferenceStoreUsageSummary


def build_summary(
    reference_store: pd.DataFrame,
    usage_scenarios: pd.DataFrame,
    lookup_results: pd.DataFrame,
    availability_review: pd.DataFrame,
    granularity_usage_review: pd.DataFrame,
    horizon_usage_review: pd.DataFrame,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> ResearchReferenceStoreUsageSummary:
    counts = _counts(lookup_results)
    scenario_count = _scenario_count(usage_scenarios)
    matched = _matched_count(lookup_results)
    availability_ratio = _first_float(availability_review, "Reference_Availability_Ratio")
    readiness_class, flag, diagnostic, follow_up = _readiness(len(reference_store), scenario_count, availability_ratio, counts)
    return ResearchReferenceStoreUsageSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        research_reference_count=len(reference_store),
        usage_scenario_count=scenario_count,
        matched_scenario_count=matched,
        unmatched_scenario_count=max(scenario_count - matched, 0),
        reference_availability_ratio=availability_ratio,
        high_quality_match_count=counts["high"],
        moderate_quality_match_count=counts["moderate"],
        low_quality_match_count=counts["low"],
        no_usable_match_count=counts["no_usable"],
        core_evidence_match_count=counts["core"],
        supporting_evidence_match_count=counts["supporting"],
        primary_usage_granularity=_primary_granularity(granularity_usage_review),
        primary_usage_horizon=_primary_horizon(horizon_usage_review),
        dominant_reference_usage_readiness_class=readiness_class,
        research_reference_store_usage_readiness_flag=flag,
        research_reference_store_usage_diagnostic=diagnostic,
        recommended_follow_up=follow_up,
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Research query interface design",
        "Current market state snapshot research workflow",
        "Expanded H4 historical data coverage",
        "Multi-pair replication",
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
        "Findings depend on local research reference store outputs.",
        "The H4 source sample may be partial due to provider row limits.",
        "Reference lookups do not imply predictive edge.",
        "Reference matches are descriptive only.",
        "No operational decision is produced.",
    ]


def _counts(frame: pd.DataFrame) -> dict[str, int]:
    if frame.empty:
        return {"high": 0, "moderate": 0, "low": 0, "no_usable": 0, "core": 0, "supporting": 0}
    return {
        "high": int((frame["Reference_Match_Quality_Class"] == "HIGH_QUALITY_REFERENCE_MATCH").sum()),
        "moderate": int((frame["Reference_Match_Quality_Class"] == "MODERATE_QUALITY_REFERENCE_MATCH").sum()),
        "low": int((frame["Reference_Match_Quality_Class"] == "LOW_QUALITY_REFERENCE_MATCH").sum()),
        "no_usable": int((frame["Reference_Match_Quality_Class"] == "NO_USABLE_REFERENCE_MATCH").sum()),
        "core": int((frame["Reference_Evidence_Quality_Class"] == "CORE_REFERENCE_EVIDENCE").sum()),
        "supporting": int((frame["Reference_Evidence_Quality_Class"] == "SUPPORTING_REFERENCE_EVIDENCE").sum()),
    }


def _scenario_count(frame: pd.DataFrame) -> int:
    if frame.empty:
        return 0
    return int((frame["Scenario_Source"] != "INPUT_MISSING").sum())


def _matched_count(frame: pd.DataFrame) -> int:
    if frame.empty:
        return 0
    matched = ~frame["Reference_Match_Level"].isin(["NO_REFERENCE_MATCH", "INPUT_MISSING"])
    return int(matched.sum())


def _first_float(frame: pd.DataFrame, column: str) -> float:
    if frame.empty or column not in frame.columns:
        return 0.0
    return round(float(pd.to_numeric(frame[column], errors="coerce").fillna(0).iloc[0]), 4)


def _primary_granularity(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "INPUT_MISSING"
    usable = frame[frame["Granularity_Usage_Class"].isin(["PRIMARY_USAGE_GRANULARITY", "SUPPORTING_USAGE_GRANULARITY"])]
    source = usable if not usable.empty else frame
    ranked = source.sort_values(["Core_Reference_Count", "Supporting_Reference_Count", "Matched_Scenario_Count"], ascending=False)
    return str(ranked.iloc[0]["Reference_Match_Level"])


def _primary_horizon(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "INPUT_MISSING"
    usable = frame[frame["Horizon_Usage_Class"].isin(["PRIMARY_USAGE_HORIZON", "SUPPORTING_USAGE_HORIZON"])]
    source = usable if not usable.empty else frame
    ranked = source.sort_values(["Core_Reference_Count", "Supporting_Reference_Count", "Matched_Scenario_Count"], ascending=False)
    return str(ranked.iloc[0]["Forward_Horizon_H4_Candles"])


def _readiness(
    reference_count: int,
    scenario_count: int,
    availability_ratio: float,
    counts: dict[str, int],
) -> tuple[str, str, str, str]:
    if reference_count == 0 or scenario_count == 0:
        return (
            "REFERENCE_USAGE_INPUT_LIMITED",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "Reference usage review needs populated reference-store and usage-scenario inputs.",
            "Research query interface design; Expanded H4 historical data coverage",
        )
    if availability_ratio >= 0.75 and counts["high"] + counts["core"] > 0:
        return (
            "REFERENCE_USAGE_READY",
            "READY_FOR_RESEARCH_QUERY_INTERFACE_DESIGN",
            "Reference store usage has broad descriptive coverage for research query design.",
            "Research query interface design; Reference stability validation",
        )
    if availability_ratio >= 0.4 and counts["moderate"] + counts["supporting"] > 0:
        return (
            "PARTIAL_REFERENCE_USAGE_READY",
            "PARTIAL_READY_FOR_RESEARCH_QUERY_INTERFACE_DESIGN",
            "Reference store usage is partially covered and remains descriptive.",
            "Current market state snapshot research workflow; Reference stability validation",
        )
    return (
        "REFERENCE_USAGE_SAMPLE_CONSTRAINED",
        "NOT_READY_REFERENCE_USAGE_SAMPLE_CONSTRAINED",
        "Reference usage is constrained by sparse descriptive matches or sample adequacy.",
        "Expanded H4 historical data coverage; Multi-pair replication",
    )
