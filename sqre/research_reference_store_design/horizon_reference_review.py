"""Forward horizon reference utility review."""

from __future__ import annotations

import pandas as pd


HORIZON_COLUMNS = [
    "Forward_Horizon_H4_Candles",
    "Candidate_Count",
    "Included_Reference_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Watchlist_Count",
    "Excluded_Count",
    "Inclusion_Ratio",
    "Horizon_Reference_Utility_Class",
    "Horizon_Reference_Diagnostic",
]


def build_horizon_reference_review(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty or "Forward_Horizon_H4_Candles" not in candidates.columns:
        return pd.DataFrame(columns=HORIZON_COLUMNS)
    rows = []
    for horizon, group in candidates.groupby("Forward_Horizon_H4_Candles", dropna=False):
        rows.append(_row(int(horizon), group))
    return pd.DataFrame(rows, columns=HORIZON_COLUMNS).sort_values(
        ["Included_Reference_Count", "Core_Reference_Count", "Candidate_Count"], ascending=False
    )


def _row(horizon: int, group: pd.DataFrame) -> dict[str, object]:
    candidate_count = len(group)
    included = int((group["Reference_Inclusion_Status"] == "INCLUDED_IN_RESEARCH_REFERENCE_STORE").sum())
    core = int((group["Reference_Tier"] == "CORE_RESEARCH_REFERENCE").sum())
    supporting = int((group["Reference_Tier"] == "SUPPORTING_RESEARCH_REFERENCE").sum())
    watchlist = int((group["Reference_Inclusion_Status"] == "WATCHLIST_ONLY").sum())
    excluded = candidate_count - included - watchlist
    ratio = round(included / candidate_count, 6) if candidate_count else 0.0
    utility = _classify(candidate_count, included, core, ratio)
    return {
        "Forward_Horizon_H4_Candles": horizon,
        "Candidate_Count": candidate_count,
        "Included_Reference_Count": included,
        "Core_Reference_Count": core,
        "Supporting_Reference_Count": supporting,
        "Watchlist_Count": watchlist,
        "Excluded_Count": excluded,
        "Inclusion_Ratio": ratio,
        "Horizon_Reference_Utility_Class": utility,
        "Horizon_Reference_Diagnostic": _diagnostic(utility),
    }


def _classify(candidate_count: int, included: int, core: int, ratio: float) -> str:
    if candidate_count == 0:
        return "INPUT_MISSING"
    if included == 0:
        return "SAMPLE_CONSTRAINED_HORIZON"
    if core > 0 and ratio >= 0.25:
        return "PRIMARY_REFERENCE_HORIZON"
    if included > 0:
        return "SUPPORTING_REFERENCE_HORIZON"
    return "LIMITED_REFERENCE_HORIZON"


def _diagnostic(utility: str) -> str:
    diagnostics = {
        "PRIMARY_REFERENCE_HORIZON": "Forward horizon has the strongest included reference support.",
        "SUPPORTING_REFERENCE_HORIZON": "Forward horizon has supporting reference rows.",
        "LIMITED_REFERENCE_HORIZON": "Forward horizon has limited reference utility.",
        "SAMPLE_CONSTRAINED_HORIZON": "Forward horizon is constrained by available historical samples.",
        "INPUT_MISSING": "Forward horizon input is missing.",
    }
    return diagnostics[utility]
