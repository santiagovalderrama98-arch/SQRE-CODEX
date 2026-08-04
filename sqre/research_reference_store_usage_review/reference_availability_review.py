"""Reference availability review."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig


AVAILABILITY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Usage_Scenario_Count",
    "Matched_Scenario_Count",
    "Unmatched_Scenario_Count",
    "Exact_D1_State_Regime_Match_Count",
    "D1_Regime_Match_Count",
    "D1_Market_State_Match_Count",
    "H4_Transition_Only_Match_Count",
    "No_Reference_Match_Count",
    "Reference_Availability_Ratio",
    "Reference_Availability_Class",
    "Availability_Diagnostic",
]


def build_reference_availability_review(
    lookup_results: pd.DataFrame,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> pd.DataFrame:
    if lookup_results.empty or bool((lookup_results["Reference_Match_Level"] == "INPUT_MISSING").all()):
        return pd.DataFrame([_row(config, 0, 0, 0, 0, 0, 0, 0, 0, "INPUT_MISSING", "Required usage inputs are missing.")])
    counts = {level: int((lookup_results["Reference_Match_Level"] == level).sum()) for level in MATCH_COUNT_LEVELS}
    matched = sum(counts[level] for level in MATCHED_LEVELS)
    scenario_count = len(lookup_results)
    ratio = matched / scenario_count if scenario_count else 0.0
    row = _row(
        config,
        scenario_count,
        matched,
        scenario_count - matched,
        counts["EXACT_D1_STATE_REGIME_CONTEXT_MATCH"],
        counts["D1_REGIME_CONTEXT_MATCH"],
        counts["D1_MARKET_STATE_CONTEXT_MATCH"],
        counts["H4_TRANSITION_ONLY_CONTEXT_MATCH"],
        counts["NO_REFERENCE_MATCH"],
        _availability_class(ratio),
        f"{matched} of {scenario_count} usage scenarios found descriptive reference rows.",
    )
    return pd.DataFrame([row], columns=AVAILABILITY_COLUMNS)


MATCHED_LEVELS = [
    "EXACT_D1_STATE_REGIME_CONTEXT_MATCH",
    "D1_REGIME_CONTEXT_MATCH",
    "D1_MARKET_STATE_CONTEXT_MATCH",
    "H4_TRANSITION_ONLY_CONTEXT_MATCH",
]
MATCH_COUNT_LEVELS = [*MATCHED_LEVELS, "NO_REFERENCE_MATCH"]


def _availability_class(ratio: float) -> str:
    if ratio >= 0.75:
        return "HIGH_REFERENCE_AVAILABILITY"
    if ratio >= 0.4:
        return "MODERATE_REFERENCE_AVAILABILITY"
    if ratio > 0:
        return "LOW_REFERENCE_AVAILABILITY"
    return "NO_REFERENCE_AVAILABILITY"


def _row(
    config: ResearchReferenceStoreUsageReviewConfig,
    scenario_count: int,
    matched: int,
    unmatched: int,
    exact: int,
    regime: int,
    state: int,
    transition: int,
    no_match: int,
    availability_class: str,
    diagnostic: str,
) -> dict[str, object]:
    return {
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "Usage_Scenario_Count": scenario_count,
        "Matched_Scenario_Count": matched,
        "Unmatched_Scenario_Count": unmatched,
        "Exact_D1_State_Regime_Match_Count": exact,
        "D1_Regime_Match_Count": regime,
        "D1_Market_State_Match_Count": state,
        "H4_Transition_Only_Match_Count": transition,
        "No_Reference_Match_Count": no_match,
        "Reference_Availability_Ratio": round(matched / scenario_count, 4) if scenario_count else 0.0,
        "Reference_Availability_Class": availability_class,
        "Availability_Diagnostic": diagnostic,
    }
