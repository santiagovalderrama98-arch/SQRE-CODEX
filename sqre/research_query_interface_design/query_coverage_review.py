"""Coverage review for research query results."""

from __future__ import annotations

import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig


COVERAGE_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Query_Request_Count",
    "Valid_Query_Count",
    "Invalid_Query_Count",
    "Query_With_Result_Count",
    "Query_Without_Result_Count",
    "Exact_D1_State_Regime_Result_Count",
    "D1_Regime_Result_Count",
    "D1_Market_State_Result_Count",
    "H4_Transition_Only_Result_Count",
    "Broader_H4_Transition_Any_Horizon_Result_Count",
    "No_Reference_Result_Count",
    "Research_Query_Coverage_Ratio",
    "Research_Query_Coverage_Class",
    "Coverage_Diagnostic",
]


def build_query_coverage_review(
    query_requests: pd.DataFrame,
    query_results: pd.DataFrame,
    config: ResearchQueryInterfaceDesignConfig,
) -> pd.DataFrame:
    request_count = len(query_requests)
    valid_count = int((query_requests.get("Query_Validation_Status", "") == "VALID_RESEARCH_QUERY").sum()) if request_count else 0
    invalid_count = request_count - valid_count
    usable = _usable_results(query_results)
    query_with_result = usable["Research_Query_ID"].nunique() if not usable.empty else 0
    query_without_result = max(request_count - query_with_result, 0)
    ratio = round(query_with_result / request_count, 4) if request_count else 0.0
    row = {
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "Query_Request_Count": request_count,
        "Valid_Query_Count": valid_count,
        "Invalid_Query_Count": invalid_count,
        "Query_With_Result_Count": query_with_result,
        "Query_Without_Result_Count": query_without_result,
        "Exact_D1_State_Regime_Result_Count": _count_level(query_results, "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH"),
        "D1_Regime_Result_Count": _count_level(query_results, "D1_REGIME_CONTEXT_QUERY_MATCH"),
        "D1_Market_State_Result_Count": _count_level(query_results, "D1_MARKET_STATE_CONTEXT_QUERY_MATCH"),
        "H4_Transition_Only_Result_Count": _count_level(query_results, "H4_TRANSITION_ONLY_QUERY_MATCH"),
        "Broader_H4_Transition_Any_Horizon_Result_Count": _count_level(
            query_results, "BROADER_H4_TRANSITION_ANY_HORIZON_QUERY_MATCH"
        ),
        "No_Reference_Result_Count": _count_level(query_results, "NO_RESEARCH_REFERENCE_QUERY_MATCH"),
        "Research_Query_Coverage_Ratio": ratio,
        "Research_Query_Coverage_Class": _coverage_class(ratio, request_count),
        "Coverage_Diagnostic": _coverage_diagnostic(ratio, request_count),
    }
    return pd.DataFrame([row], columns=COVERAGE_COLUMNS)


def _usable_results(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    return frame[
        ~frame["Research_Query_Match_Level"].isin(["NO_RESEARCH_REFERENCE_QUERY_MATCH", "INPUT_MISSING"])
    ].copy()


def _count_level(frame: pd.DataFrame, level: str) -> int:
    if frame.empty:
        return 0
    return int((frame["Research_Query_Match_Level"] == level).sum())


def _coverage_class(ratio: float, request_count: int) -> str:
    if request_count == 0:
        return "INPUT_MISSING"
    if ratio >= 0.75:
        return "HIGH_RESEARCH_QUERY_COVERAGE"
    if ratio >= 0.40:
        return "MODERATE_RESEARCH_QUERY_COVERAGE"
    if ratio > 0:
        return "LOW_RESEARCH_QUERY_COVERAGE"
    return "NO_RESEARCH_QUERY_COVERAGE"


def _coverage_diagnostic(ratio: float, request_count: int) -> str:
    if request_count == 0:
        return "No research query requests were available."
    return f"Descriptive reference coverage ratio is {ratio:.4f}."

