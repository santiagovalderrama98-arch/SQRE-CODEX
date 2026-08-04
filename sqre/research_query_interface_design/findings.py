"""Summary findings for Research Query Interface Design."""

from __future__ import annotations

import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.models import ResearchQueryInterfaceDesignSummary


def build_summary(
    reference_store: pd.DataFrame,
    query_requests: pd.DataFrame,
    query_results: pd.DataFrame,
    coverage_review: pd.DataFrame,
    config: ResearchQueryInterfaceDesignConfig,
) -> ResearchQueryInterfaceDesignSummary:
    request_count = len(query_requests)
    valid_count = int((query_requests.get("Query_Validation_Status", "") == "VALID_RESEARCH_QUERY").sum()) if request_count else 0
    usable = query_results[
        ~query_results["Research_Query_Match_Level"].isin(["NO_RESEARCH_REFERENCE_QUERY_MATCH", "INPUT_MISSING"])
    ] if not query_results.empty else pd.DataFrame()
    query_with_result = usable["Research_Query_ID"].nunique() if not usable.empty else 0
    coverage_ratio = _first_float(coverage_review, "Research_Query_Coverage_Ratio")
    readiness_class, flag, diagnostic, follow_up = _readiness(query_results, coverage_ratio, request_count, len(reference_store))
    return ResearchQueryInterfaceDesignSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        research_reference_count=len(reference_store),
        research_query_request_count=request_count,
        valid_query_request_count=valid_count,
        query_result_count=len(query_results),
        query_with_result_count=query_with_result,
        query_without_result_count=max(request_count - query_with_result, 0),
        research_query_coverage_ratio=coverage_ratio,
        high_quality_query_result_count=_count(query_results, "Research_Query_Result_Quality_Class", "HIGH_QUALITY_RESEARCH_QUERY_RESULT"),
        moderate_quality_query_result_count=_count(
            query_results, "Research_Query_Result_Quality_Class", "MODERATE_QUALITY_RESEARCH_QUERY_RESULT"
        ),
        low_quality_query_result_count=_count(query_results, "Research_Query_Result_Quality_Class", "LOW_QUALITY_RESEARCH_QUERY_RESULT"),
        no_usable_query_result_count=_count(
            query_results, "Research_Query_Result_Quality_Class", "NO_USABLE_RESEARCH_QUERY_RESULT"
        ),
        core_evidence_query_result_count=_count(query_results, "Research_Query_Evidence_Class", "CORE_RESEARCH_REFERENCE_EVIDENCE"),
        supporting_evidence_query_result_count=_count(
            query_results, "Research_Query_Evidence_Class", "SUPPORTING_RESEARCH_REFERENCE_EVIDENCE"
        ),
        primary_query_match_level=_primary(query_results, "Research_Query_Match_Level"),
        primary_query_horizon=_primary(query_results, "Matched_Forward_Horizon_H4_Candles"),
        dominant_research_query_interface_readiness_class=readiness_class,
        research_query_interface_readiness_flag=flag,
        research_query_interface_diagnostic=diagnostic,
        recommended_follow_up=follow_up,
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Current market state snapshot research workflow",
        "Reference stability validation",
        "Expanded H4 historical data coverage",
        "Multi-pair replication",
        "Research query interface documentation",
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
        "Findings depend on local research reference store and usage review outputs.",
        "The H4 source sample may be partial due to provider row limits.",
        "Query matches do not imply predictive edge.",
        "Query results are descriptive only.",
        "No operational decision is produced.",
    ]


def _readiness(
    query_results: pd.DataFrame,
    coverage_ratio: float,
    request_count: int,
    reference_count: int,
) -> tuple[str, str, str, str]:
    if request_count == 0 or reference_count == 0:
        return (
            "RESEARCH_QUERY_INTERFACE_INPUT_LIMITED",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "Required research query or reference-store inputs are limited.",
            "Research reference store completeness review",
        )
    high = _count(query_results, "Research_Query_Result_Quality_Class", "HIGH_QUALITY_RESEARCH_QUERY_RESULT")
    moderate = _count(query_results, "Research_Query_Result_Quality_Class", "MODERATE_QUALITY_RESEARCH_QUERY_RESULT")
    low = _count(query_results, "Research_Query_Result_Quality_Class", "LOW_QUALITY_RESEARCH_QUERY_RESULT")
    if coverage_ratio >= 0.75 and high > 0:
        return (
            "RESEARCH_QUERY_INTERFACE_READY",
            "READY_FOR_CURRENT_MARKET_STATE_SNAPSHOT_RESEARCH_WORKFLOW",
            "Research query interface has broad descriptive reference coverage.",
            "Current market state snapshot research workflow",
        )
    if coverage_ratio >= 0.40 and (moderate > 0 or high > 0):
        return (
            "PARTIAL_RESEARCH_QUERY_INTERFACE_READY",
            "PARTIAL_READY_FOR_CURRENT_MARKET_STATE_SNAPSHOT_RESEARCH_WORKFLOW",
            "Research query interface has partial descriptive reference coverage.",
            "Reference stability validation",
        )
    if low > 0 or coverage_ratio > 0:
        return (
            "RESEARCH_QUERY_INTERFACE_SAMPLE_CONSTRAINED",
            "NOT_READY_RESEARCH_QUERY_SAMPLE_CONSTRAINED",
            "Research query interface is constrained by limited or dispersed evidence.",
            "Expanded H4 historical data coverage",
        )
    return (
        "RESEARCH_QUERY_INTERFACE_INPUT_LIMITED",
        "NOT_READY_RESEARCH_QUERY_INPUT_LIMITED",
        "Research query interface has insufficient matched descriptive references.",
        "Expanded H4 historical data coverage",
    )


def _count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column] == value).sum())


def _primary(frame: pd.DataFrame, column: str) -> str:
    if frame.empty or column not in frame.columns:
        return "INPUT_MISSING"
    usable = frame[~frame["Research_Query_Match_Level"].isin(["NO_RESEARCH_REFERENCE_QUERY_MATCH", "INPUT_MISSING"])]
    if usable.empty:
        return "NO_RESEARCH_REFERENCE_QUERY_MATCH"
    counts = usable[column].astype(str).value_counts()
    return str(counts.index[0]) if not counts.empty else "INPUT_MISSING"


def _first_float(frame: pd.DataFrame, column: str) -> float:
    if frame.empty or column not in frame.columns:
        return 0.0
    return float(frame.iloc[0].get(column, 0.0))

