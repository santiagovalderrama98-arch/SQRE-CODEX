"""Build exclusion and watchlist review rows."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_design.reference_tier_classifier import INCLUDED_STATUS


EXCLUSION_COLUMNS = [
    "Research_Reference_Candidate_ID",
    "Outcome_Profile_ID",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "Forward_Horizon_H4_Candles",
    "Outcome_Sample_Size",
    "Outcome_Dispersion_Pips",
    "Outcome_Interpretability_Class",
    "Reference_Tier",
    "Reference_Inclusion_Status",
    "Exclusion_Reason_Class",
    "Exclusion_Diagnostic",
    "Recommended_Follow_Up",
]


def build_reference_exclusion_review(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(columns=EXCLUSION_COLUMNS)
    selected = candidates[candidates["Reference_Inclusion_Status"] != INCLUDED_STATUS]
    rows = []
    for _, row in selected.iterrows():
        reason, follow_up = _reason_and_follow_up(row)
        rows.append(
            {
                **{column: row.get(column, "") for column in EXCLUSION_COLUMNS if column not in _DERIVED_COLUMNS},
                "Exclusion_Reason_Class": reason,
                "Exclusion_Diagnostic": _diagnostic(reason),
                "Recommended_Follow_Up": follow_up,
            }
        )
    return pd.DataFrame(rows, columns=EXCLUSION_COLUMNS)


_DERIVED_COLUMNS = {"Exclusion_Reason_Class", "Exclusion_Diagnostic", "Recommended_Follow_Up"}


def _reason_and_follow_up(row: pd.Series) -> tuple[str, str]:
    tier = str(row.get("Reference_Tier", ""))
    diagnostic = str(row.get("Reference_Diagnostic", "")).lower()
    if tier == "EXCLUDED_SAMPLE_CONSTRAINED":
        return "SAMPLE_CONSTRAINED", "EXPAND_HISTORICAL_SAMPLE"
    if tier == "EXCLUDED_HIGH_DISPERSION":
        return "HIGH_DISPERSION", "REVIEW_DISPERSION_BEHAVIOR"
    if tier == "EXCLUDED_LOW_INTERPRETABILITY":
        return "LOW_INTERPRETABILITY", "REVIEW_CONTEXT_GRANULARITY"
    if tier == "INPUT_MISSING":
        return "INPUT_MISSING", "REVIEW_INPUT_COMPLETENESS"
    if "horizon" in diagnostic:
        return "UNSTABLE_HORIZON_CONTEXT", "REVIEW_HORIZON_STABILITY"
    return "WATCHLIST_LIMITED_EVIDENCE", "REVIEW_HORIZON_STABILITY"


def _diagnostic(reason: str) -> str:
    diagnostics = {
        "SAMPLE_CONSTRAINED": "Profile is excluded because sample depth is limited.",
        "HIGH_DISPERSION": "Profile is excluded because observed dispersion is high.",
        "LOW_INTERPRETABILITY": "Profile is excluded because interpretability is limited.",
        "UNSTABLE_HORIZON_CONTEXT": "Profile is retained for watchlist review because horizon behavior is unstable.",
        "WATCHLIST_LIMITED_EVIDENCE": "Profile is retained only for watchlist review due to limited supporting evidence.",
        "INPUT_MISSING": "Required interpretation inputs are missing.",
    }
    return diagnostics[reason]
