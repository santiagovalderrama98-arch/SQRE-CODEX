"""Lookup historical references for snapshot query requests."""

from __future__ import annotations

import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.snapshot_reference_ranker import rank_snapshot_reference_candidates
from sqre.current_market_state_snapshot_research.snapshot_query_builder import SNAPSHOT_QUERY_COLUMNS
from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.query_evidence_builder import classify_evidence, classify_result_quality
from sqre.research_query_interface_design.query_fallback_engine import TRACE_COLUMNS, find_research_reference_matches
from sqre.research_reference_store_usage_review.reference_query_builder import float_value, int_value, text_value


SNAPSHOT_REFERENCE_RESULT_COLUMNS = [
    "Snapshot_Reference_Result_ID",
    "Snapshot_Query_ID",
    "Snapshot_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Requested_Forward_Horizon_H4_Candles",
    "Matched_Research_Reference_ID",
    "Matched_Outcome_Profile_ID",
    "Matched_Context_Granularity",
    "Matched_Reference_Tier",
    "Matched_Forward_Horizon_H4_Candles",
    "Matched_Outcome_Sample_Size",
    "Matched_Outcome_Dispersion_Pips",
    "Matched_Mean_Forward_Close_Change_Pips",
    "Matched_Median_Forward_Close_Change_Pips",
    "Matched_Directional_Behavior_Class",
    "Matched_Dominant_Observed_Direction",
    "Matched_Excursion_Behavior_Class",
    "Matched_Horizon_Stability_Class",
    "Snapshot_Query_Match_Level",
    "Snapshot_Research_Result_Class",
    "Snapshot_Evidence_Class",
    "Result_Rank",
    "Snapshot_Result_Diagnostic",
]
SNAPSHOT_FALLBACK_TRACE_COLUMNS = [
    "Snapshot_Query_ID",
    "Fallback_Attempt_Order",
    "Attempted_Match_Level",
    "Attempted_H4_Transition_Label",
    "Attempted_D1_Market_State",
    "Attempted_D1_Regime_Label",
    "Attempted_Forward_Horizon_H4_Candles",
    "Candidate_Reference_Count",
    "Selected_Result_Count",
    "Fallback_Attempt_Status",
    "Fallback_Diagnostic",
]


def lookup_snapshot_references(
    snapshot_queries: pd.DataFrame,
    reference_store: pd.DataFrame,
    config: CurrentMarketStateSnapshotResearchConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    result_rows: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []
    sequence = 1
    query_config = _query_config(config)
    for _, snapshot_query in snapshot_queries.iterrows():
        query = _to_research_query(snapshot_query)
        matches, traces, match_level = find_research_reference_matches(query, reference_store, query_config)
        trace_rows.extend(_to_snapshot_trace(traces))
        if matches.empty:
            result_rows.append(_empty_result(sequence, snapshot_query, match_level))
            sequence += 1
            continue
        ranked = rank_snapshot_reference_candidates(matches).head(config.maximum_results_per_snapshot_query)
        for rank, (_, match) in enumerate(ranked.iterrows(), start=1):
            result_rows.append(_result(sequence, snapshot_query, match, match_level, rank, query_config))
            sequence += 1
    return (
        pd.DataFrame(result_rows, columns=SNAPSHOT_REFERENCE_RESULT_COLUMNS),
        pd.DataFrame(trace_rows, columns=SNAPSHOT_FALLBACK_TRACE_COLUMNS),
    )


def _query_config(config: CurrentMarketStateSnapshotResearchConfig) -> ResearchQueryInterfaceDesignConfig:
    return ResearchQueryInterfaceDesignConfig(
        reference_store_dir=config.reference_store_dir,
        output_dir=config.output_dir,
        report_path=config.report_path,
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        preferred_horizons=config.preferred_horizons,
        maximum_results_per_query=config.maximum_results_per_snapshot_query,
        minimum_reference_sample_size=config.minimum_reference_sample_size,
        minimum_core_reference_sample_size=config.minimum_core_reference_sample_size,
        maximum_reference_dispersion_pips=config.maximum_reference_dispersion_pips,
    )


def _to_research_query(snapshot_query: pd.Series) -> pd.Series:
    status = text_value(snapshot_query.get("Snapshot_Query_Validation_Status", ""))
    query_status = {
        "VALID_SNAPSHOT_QUERY": "VALID_RESEARCH_QUERY",
        "INPUT_MISSING": "INPUT_MISSING",
    }.get(status, "INVALID_RESEARCH_QUERY")
    return pd.Series(
        {
            "Research_Query_ID": text_value(snapshot_query.get("Snapshot_Query_ID", "")),
            "Query_Validation_Status": query_status,
            "H4_Transition_Label": text_value(snapshot_query.get("H4_Transition_Label", "")),
            "D1_Market_State": text_value(snapshot_query.get("D1_Market_State", "")),
            "D1_Regime_Label": text_value(snapshot_query.get("D1_Regime_Label", "")),
            "Requested_Forward_Horizon_H4_Candles": int_value(
                snapshot_query.get("Requested_Forward_Horizon_H4_Candles", 0)
            ),
        }
    )


def _result(
    sequence: int,
    query: pd.Series,
    match: pd.Series,
    match_level: str,
    rank: int,
    query_config: ResearchQueryInterfaceDesignConfig,
) -> dict[str, object]:
    sample_size = int_value(match.get("Outcome_Sample_Size", 0))
    dispersion = float_value(match.get("Outcome_Dispersion_Pips", 0.0))
    tier = text_value(match.get("Reference_Tier", ""))
    quality = _snapshot_result_class(classify_result_quality(match_level, sample_size, dispersion, query_config))
    evidence = _snapshot_evidence_class(classify_evidence(tier, sample_size, dispersion, query_config))
    return {
        **_query_fields(sequence, query),
        "Matched_Research_Reference_ID": text_value(match.get("Research_Reference_ID", "")),
        "Matched_Outcome_Profile_ID": text_value(match.get("Outcome_Profile_ID", "")),
        "Matched_Context_Granularity": text_value(match.get("Context_Granularity", "")),
        "Matched_Reference_Tier": tier,
        "Matched_Forward_Horizon_H4_Candles": int_value(match.get("Forward_Horizon_H4_Candles", 0)),
        "Matched_Outcome_Sample_Size": sample_size,
        "Matched_Outcome_Dispersion_Pips": dispersion,
        "Matched_Mean_Forward_Close_Change_Pips": float_value(match.get("Mean_Forward_Close_Change_Pips", 0.0)),
        "Matched_Median_Forward_Close_Change_Pips": float_value(match.get("Median_Forward_Close_Change_Pips", 0.0)),
        "Matched_Directional_Behavior_Class": text_value(match.get("Directional_Behavior_Class", "")),
        "Matched_Dominant_Observed_Direction": text_value(match.get("Dominant_Observed_Direction", "")),
        "Matched_Excursion_Behavior_Class": text_value(match.get("Excursion_Behavior_Class", "")),
        "Matched_Horizon_Stability_Class": text_value(match.get("Horizon_Stability_Class", "")),
        "Snapshot_Query_Match_Level": match_level,
        "Snapshot_Research_Result_Class": quality,
        "Snapshot_Evidence_Class": evidence,
        "Result_Rank": rank,
        "Snapshot_Result_Diagnostic": f"Descriptive historical reference matched using {match_level}.",
    }


def _empty_result(sequence: int, query: pd.Series, match_level: str) -> dict[str, object]:
    quality = "INPUT_MISSING" if match_level == "INPUT_MISSING" else "NO_USABLE_SNAPSHOT_REFERENCE"
    evidence = "INPUT_MISSING" if match_level == "INPUT_MISSING" else "INSUFFICIENT_SNAPSHOT_REFERENCE_EVIDENCE"
    return {
        **_query_fields(sequence, query),
        "Matched_Research_Reference_ID": "",
        "Matched_Outcome_Profile_ID": "",
        "Matched_Context_Granularity": "",
        "Matched_Reference_Tier": "",
        "Matched_Forward_Horizon_H4_Candles": 0,
        "Matched_Outcome_Sample_Size": 0,
        "Matched_Outcome_Dispersion_Pips": 0.0,
        "Matched_Mean_Forward_Close_Change_Pips": 0.0,
        "Matched_Median_Forward_Close_Change_Pips": 0.0,
        "Matched_Directional_Behavior_Class": "",
        "Matched_Dominant_Observed_Direction": "",
        "Matched_Excursion_Behavior_Class": "",
        "Matched_Horizon_Stability_Class": "",
        "Snapshot_Query_Match_Level": match_level,
        "Snapshot_Research_Result_Class": quality,
        "Snapshot_Evidence_Class": evidence,
        "Result_Rank": 0,
        "Snapshot_Result_Diagnostic": "No descriptive historical reference matched this snapshot query.",
    }


def _query_fields(sequence: int, query: pd.Series) -> dict[str, object]:
    return {
        "Snapshot_Reference_Result_ID": f"CMSR_{sequence:06d}",
        "Snapshot_Query_ID": text_value(query.get("Snapshot_Query_ID", "")),
        "Snapshot_ID": text_value(query.get("Snapshot_ID", "")),
        "Symbol": text_value(query.get("Symbol", "")),
        "H4_Timeframe": text_value(query.get("H4_Timeframe", "")),
        "D1_Timeframe": text_value(query.get("D1_Timeframe", "")),
        "H4_Transition_Label": text_value(query.get("H4_Transition_Label", "")),
        "D1_Market_State": text_value(query.get("D1_Market_State", "")),
        "D1_Regime_Label": text_value(query.get("D1_Regime_Label", "")),
        "D1_Structure_Direction": text_value(query.get("D1_Structure_Direction", "")),
        "Requested_Forward_Horizon_H4_Candles": int_value(query.get("Requested_Forward_Horizon_H4_Candles", 0)),
    }


def _to_snapshot_trace(traces: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for trace in traces:
        row = {column: trace.get(column, "") for column in TRACE_COLUMNS}
        row["Snapshot_Query_ID"] = row.pop("Research_Query_ID", "")
        rows.append(row)
    return rows


def _snapshot_result_class(quality: str) -> str:
    return {
        "HIGH_QUALITY_RESEARCH_QUERY_RESULT": "HIGH_EVIDENCE_SNAPSHOT_REFERENCE",
        "MODERATE_QUALITY_RESEARCH_QUERY_RESULT": "MODERATE_EVIDENCE_SNAPSHOT_REFERENCE",
        "LOW_QUALITY_RESEARCH_QUERY_RESULT": "LOW_EVIDENCE_SNAPSHOT_REFERENCE",
        "NO_USABLE_RESEARCH_QUERY_RESULT": "NO_USABLE_SNAPSHOT_REFERENCE",
        "INPUT_MISSING": "INPUT_MISSING",
    }.get(quality, "LOW_EVIDENCE_SNAPSHOT_REFERENCE")


def _snapshot_evidence_class(evidence: str) -> str:
    return {
        "CORE_RESEARCH_REFERENCE_EVIDENCE": "CORE_SNAPSHOT_REFERENCE_EVIDENCE",
        "SUPPORTING_RESEARCH_REFERENCE_EVIDENCE": "SUPPORTING_SNAPSHOT_REFERENCE_EVIDENCE",
        "WATCHLIST_RESEARCH_REFERENCE_EVIDENCE": "WATCHLIST_SNAPSHOT_REFERENCE_EVIDENCE",
        "INSUFFICIENT_RESEARCH_REFERENCE_EVIDENCE": "INSUFFICIENT_SNAPSHOT_REFERENCE_EVIDENCE",
        "INPUT_MISSING": "INPUT_MISSING",
    }.get(evidence, "INSUFFICIENT_SNAPSHOT_REFERENCE_EVIDENCE")
