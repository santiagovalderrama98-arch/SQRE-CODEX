"""Rank research query result candidates."""

from __future__ import annotations

import pandas as pd


def rank_reference_candidates(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return candidates
    ranked = candidates.copy()
    tier_order = {"CORE_REFERENCE": 0, "SUPPORTING_REFERENCE": 1, "WATCHLIST_REFERENCE": 2}
    ranked["_tier_order"] = ranked.get("Reference_Tier", "").map(lambda item: tier_order.get(str(item).strip().upper(), 9))
    ranked["_sample_order"] = pd.to_numeric(ranked.get("Outcome_Sample_Size", 0), errors="coerce").fillna(0)
    ranked["_dispersion_order"] = pd.to_numeric(ranked.get("Outcome_Dispersion_Pips", 0), errors="coerce").fillna(0)
    return ranked.sort_values(["_tier_order", "_sample_order", "_dispersion_order"], ascending=[True, False, True])
