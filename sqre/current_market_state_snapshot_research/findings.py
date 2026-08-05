"""Summary findings for Current Market State Snapshot Research."""

from __future__ import annotations

import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.models import CurrentMarketStateSnapshotResearchSummary


def build_summary(
    reference_store: pd.DataFrame,
    snapshot_context: pd.DataFrame,
    snapshot_queries: pd.DataFrame,
    snapshot_results: pd.DataFrame,
    config: CurrentMarketStateSnapshotResearchConfig,
) -> CurrentMarketStateSnapshotResearchSummary:
    matched_query_ids = _matched_query_ids(snapshot_results)
    query_count = len(snapshot_queries)
    query_with = len(matched_query_ids)
    query_without = max(query_count - query_with, 0)
    high = _count(snapshot_results, "Snapshot_Research_Result_Class", "HIGH_EVIDENCE_SNAPSHOT_REFERENCE")
    moderate = _count(snapshot_results, "Snapshot_Research_Result_Class", "MODERATE_EVIDENCE_SNAPSHOT_REFERENCE")
    low = _count(snapshot_results, "Snapshot_Research_Result_Class", "LOW_EVIDENCE_SNAPSHOT_REFERENCE")
    no_usable = _count(snapshot_results, "Snapshot_Research_Result_Class", "NO_USABLE_SNAPSHOT_REFERENCE")
    core = _count(snapshot_results, "Snapshot_Evidence_Class", "CORE_SNAPSHOT_REFERENCE_EVIDENCE")
    supporting = _count(snapshot_results, "Snapshot_Evidence_Class", "SUPPORTING_SNAPSHOT_REFERENCE_EVIDENCE")
    readiness_class, readiness_flag, diagnostic = _readiness(query_count, query_with, high, moderate, low, no_usable)
    context = snapshot_context.iloc[0] if not snapshot_context.empty else pd.Series(dtype=object)
    return CurrentMarketStateSnapshotResearchSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        snapshot_mode=str(context.get("Snapshot_Mode", "INPUT_MISSING")),
        snapshot_source=str(context.get("Snapshot_Source", "INPUT_MISSING")),
        snapshot_timestamp=str(context.get("Snapshot_Timestamp", "")),
        snapshot_timestamp_status=str(context.get("Snapshot_Timestamp_Status", "INPUT_MISSING")),
        snapshot_validation_status=str(context.get("Snapshot_Validation_Status", "INPUT_MISSING")),
        research_reference_count=len(reference_store),
        snapshot_query_count=query_count,
        snapshot_result_count=len(snapshot_results),
        snapshot_query_with_result_count=query_with,
        snapshot_query_without_result_count=query_without,
        snapshot_reference_coverage_ratio=round(query_with / query_count, 4) if query_count else 0.0,
        high_evidence_snapshot_result_count=high,
        moderate_evidence_snapshot_result_count=moderate,
        low_evidence_snapshot_result_count=low,
        no_usable_snapshot_result_count=no_usable,
        core_evidence_snapshot_result_count=core,
        supporting_evidence_snapshot_result_count=supporting,
        primary_snapshot_query_match_level=_mode(snapshot_results, "Snapshot_Query_Match_Level"),
        primary_snapshot_horizon=_mode(snapshot_results, "Matched_Forward_Horizon_H4_Candles"),
        dominant_current_market_state_snapshot_readiness_class=readiness_class,
        current_market_state_snapshot_readiness_flag=readiness_flag,
        current_market_state_snapshot_diagnostic=diagnostic,
        recommended_follow_up=recommended_follow_up(readiness_flag),
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Research dashboard prototype",
        "Reference stability validation",
        "Expanded H4 historical data coverage",
        "Multi-pair replication",
        "Live data snapshot integration design",
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
        "Findings depend on local research reference store and query interface outputs.",
        "Latest available snapshot may not reflect live market conditions.",
        "The H4 source sample may be partial due to provider row limits.",
        "Snapshot matches do not imply predictive edge.",
        "Snapshot results are descriptive only.",
        "No operational decision is produced.",
    ]


def recommended_follow_up(readiness_flag: str) -> str:
    if readiness_flag == "READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE":
        return "Research dashboard prototype; Reference stability validation"
    if readiness_flag == "PARTIAL_READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE":
        return "Manual research review; Reference stability validation"
    return "Expanded H4 historical data coverage; Reference stability validation"


def _readiness(
    query_count: int, query_with: int, high: int, moderate: int, low: int, no_usable: int
) -> tuple[str, str, str]:
    if query_count == 0:
        return (
            "INPUT_MISSING",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "No snapshot query requests were available for reference lookup.",
        )
    if query_with == 0:
        return (
            "CURRENT_MARKET_STATE_SNAPSHOT_INPUT_LIMITED",
            "NOT_READY_SNAPSHOT_INPUT_LIMITED",
            "Snapshot workflow found no descriptive historical references.",
        )
    if high > 0 or moderate > 0:
        return (
            "CURRENT_MARKET_STATE_SNAPSHOT_RESEARCH_READY",
            "READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE",
            "Snapshot workflow has descriptive historical references for research review.",
        )
    if low > 0:
        return (
            "PARTIAL_CURRENT_MARKET_STATE_SNAPSHOT_RESEARCH_READY",
            "PARTIAL_READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE",
            "Snapshot workflow has limited descriptive references that require review.",
        )
    return (
        "CURRENT_MARKET_STATE_SNAPSHOT_SAMPLE_CONSTRAINED",
        "NOT_READY_SNAPSHOT_SAMPLE_CONSTRAINED",
        f"{no_usable} snapshot reference results were not usable for descriptive review.",
    )


def _matched_query_ids(snapshot_results: pd.DataFrame) -> set[str]:
    if snapshot_results.empty:
        return set()
    return set(
        snapshot_results.loc[
            snapshot_results["Matched_Research_Reference_ID"].astype(str) != "",
            "Snapshot_Query_ID",
        ].astype(str)
    )


def _count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column] == value).sum())


def _mode(frame: pd.DataFrame, column: str) -> str:
    if frame.empty or column not in frame.columns:
        return ""
    values = frame[column].replace("", pd.NA).dropna()
    if values.empty:
        return ""
    return str(values.value_counts().idxmax())
