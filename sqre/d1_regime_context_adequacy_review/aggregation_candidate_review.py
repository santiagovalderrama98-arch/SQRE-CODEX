"""Identify D1 context grouping candidates for later research review."""

from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig


AGGREGATION_CANDIDATE_COLUMNS = [
    "Aggregation_Candidate_ID",
    "Candidate_Type",
    "D1_Market_State",
    "D1_Regime_Label",
    "Affected_H4_Transition_Count",
    "Affected_Context_Profile_Count",
    "Low_Or_Insufficient_Context_Count",
    "Research_Ready_Context_Count",
    "Fragmentation_Evidence_Class",
    "Aggregation_Candidate_Class",
    "Candidate_Diagnostic",
    "Recommended_Follow_Up",
]


def build_aggregation_candidate_review(
    profiles: pd.DataFrame,
    config: D1RegimeContextAdequacyReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=AGGREGATION_CANDIDATE_COLUMNS)
    rows: list[dict[str, object]] = []
    rows.extend(_context_candidates(profiles, "D1_MARKET_STATE", "D1_Market_State", config, start_index=1))
    rows.extend(
        _context_candidates(
            profiles,
            "D1_REGIME_LABEL",
            "D1_Regime_Label",
            config,
            start_index=len(rows) + 1,
        )
    )
    if not rows:
        rows.append(_global_limitation_row())
    return pd.DataFrame(rows, columns=AGGREGATION_CANDIDATE_COLUMNS)


def _context_candidates(
    profiles: pd.DataFrame,
    candidate_type: str,
    column: str,
    config: D1RegimeContextAdequacyReviewConfig,
    *,
    start_index: int,
) -> list[dict[str, object]]:
    rows = []
    for offset, (value, group) in enumerate(profiles.groupby(column, dropna=False), start=start_index):
        ready = int((group["Context_Sample_Adequacy_Class"] == "RESEARCH_READY_CONTEXT_SAMPLE").sum())
        low = int(
            group["Context_Sample_Adequacy_Class"].isin(["LOW_CONTEXT_SAMPLE", "INSUFFICIENT_CONTEXT_SAMPLE"]).sum()
        )
        profile_count = len(group)
        if profile_count == 0:
            continue
        low_ratio = low / profile_count
        if low_ratio < config.fragmentation_ratio_threshold:
            continue
        candidate_class = (
            "REVIEW_D1_MARKET_STATE_AGGREGATION"
            if candidate_type == "D1_MARKET_STATE"
            else "REVIEW_D1_REGIME_AGGREGATION"
        )
        rows.append(
            {
                "Aggregation_Candidate_ID": f"D1_AGG_CANDIDATE_{offset:06d}",
                "Candidate_Type": candidate_type,
                "D1_Market_State": value if candidate_type == "D1_MARKET_STATE" else "",
                "D1_Regime_Label": value if candidate_type == "D1_REGIME_LABEL" else "",
                "Affected_H4_Transition_Count": int(group["H4_Transition_Label"].nunique()),
                "Affected_Context_Profile_Count": profile_count,
                "Low_Or_Insufficient_Context_Count": low,
                "Research_Ready_Context_Count": ready,
                "Fragmentation_Evidence_Class": _evidence_class(low_ratio),
                "Aggregation_Candidate_Class": candidate_class,
                "Candidate_Diagnostic": "D1 context grouping may need later research review due to constrained profiles.",
                "Recommended_Follow_Up": "D1_REGIME_GROUPING_RESEARCH"
                if candidate_type == "D1_REGIME_LABEL"
                else "D1_MARKET_STATE_GROUPING_RESEARCH",
            }
        )
    return rows


def _evidence_class(low_ratio: float) -> str:
    if low_ratio >= 0.90:
        return "EXTREME_FRAGMENTATION_EVIDENCE"
    if low_ratio >= 0.70:
        return "HIGH_FRAGMENTATION_EVIDENCE"
    return "MODERATE_FRAGMENTATION_EVIDENCE"


def _global_limitation_row() -> dict[str, object]:
    return {
        "Aggregation_Candidate_ID": "D1_AGG_CANDIDATE_000001",
        "Candidate_Type": "GLOBAL_SAMPLE_LIMITATION",
        "D1_Market_State": "",
        "D1_Regime_Label": "",
        "Affected_H4_Transition_Count": 0,
        "Affected_Context_Profile_Count": 0,
        "Low_Or_Insufficient_Context_Count": 0,
        "Research_Ready_Context_Count": 0,
        "Fragmentation_Evidence_Class": "INPUT_LIMITED",
        "Aggregation_Candidate_Class": "INPUT_LIMITED",
        "Candidate_Diagnostic": "No aggregation candidates were identified from available inputs.",
        "Recommended_Follow_Up": "EXPANDED_H4_HISTORICAL_DATA_COVERAGE",
    }
