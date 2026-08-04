"""Context granularity reference utility review."""

from __future__ import annotations

import pandas as pd


GRANULARITY_COLUMNS = [
    "Context_Granularity",
    "Candidate_Count",
    "Included_Reference_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Watchlist_Count",
    "Excluded_Count",
    "Inclusion_Ratio",
    "Granularity_Reference_Utility_Class",
    "Granularity_Reference_Diagnostic",
]


def build_granularity_reference_review(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty or "Context_Granularity" not in candidates.columns:
        return pd.DataFrame(columns=GRANULARITY_COLUMNS)
    rows = []
    for granularity, group in candidates.groupby("Context_Granularity", dropna=False):
        rows.append(_row(str(granularity), group))
    return pd.DataFrame(rows, columns=GRANULARITY_COLUMNS).sort_values(
        ["Included_Reference_Count", "Core_Reference_Count", "Candidate_Count"], ascending=False
    )


def _row(granularity: str, group: pd.DataFrame) -> dict[str, object]:
    candidate_count = len(group)
    included = int((group["Reference_Inclusion_Status"] == "INCLUDED_IN_RESEARCH_REFERENCE_STORE").sum())
    core = int((group["Reference_Tier"] == "CORE_RESEARCH_REFERENCE").sum())
    supporting = int((group["Reference_Tier"] == "SUPPORTING_RESEARCH_REFERENCE").sum())
    watchlist = int((group["Reference_Inclusion_Status"] == "WATCHLIST_ONLY").sum())
    excluded = candidate_count - included - watchlist
    ratio = round(included / candidate_count, 6) if candidate_count else 0.0
    utility = _classify(candidate_count, included, core, ratio)
    return {
        "Context_Granularity": granularity,
        "Candidate_Count": candidate_count,
        "Included_Reference_Count": included,
        "Core_Reference_Count": core,
        "Supporting_Reference_Count": supporting,
        "Watchlist_Count": watchlist,
        "Excluded_Count": excluded,
        "Inclusion_Ratio": ratio,
        "Granularity_Reference_Utility_Class": utility,
        "Granularity_Reference_Diagnostic": _diagnostic(utility),
    }


def _classify(candidate_count: int, included: int, core: int, ratio: float) -> str:
    if candidate_count == 0:
        return "INPUT_MISSING"
    if included == 0:
        return "SAMPLE_CONSTRAINED_GRANULARITY"
    if core > 0 and ratio >= 0.25:
        return "PRIMARY_REFERENCE_GRANULARITY"
    if included > 0:
        return "SUPPORTING_REFERENCE_GRANULARITY"
    return "LIMITED_REFERENCE_GRANULARITY"


def _diagnostic(utility: str) -> str:
    diagnostics = {
        "PRIMARY_REFERENCE_GRANULARITY": "Granularity has the strongest included reference support.",
        "SUPPORTING_REFERENCE_GRANULARITY": "Granularity has supporting reference rows.",
        "LIMITED_REFERENCE_GRANULARITY": "Granularity has limited reference utility.",
        "SAMPLE_CONSTRAINED_GRANULARITY": "Granularity is constrained by available historical samples.",
        "INPUT_MISSING": "Granularity input is missing.",
    }
    return diagnostics[utility]
