"""Context granularity utility review for H4/D1 forward outcomes."""

from __future__ import annotations

import pandas as pd


GRANULARITY_COLUMNS = [
    "Context_Granularity",
    "Outcome_Profile_Count",
    "Research_Ready_Profile_Count",
    "Moderate_Profile_Count",
    "Low_Or_Insufficient_Profile_Count",
    "Interpretable_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "Context_Granularity_Utility_Class",
    "Granularity_Utility_Diagnostic",
]


def build_context_granularity_utility_review(
    interpretability_review: pd.DataFrame,
) -> pd.DataFrame:
    if interpretability_review.empty:
        return pd.DataFrame(columns=GRANULARITY_COLUMNS)
    rows = []
    for granularity, group in interpretability_review.groupby("Context_Granularity", dropna=False):
        rows.append(_row(str(granularity), group))
    return pd.DataFrame(rows, columns=GRANULARITY_COLUMNS)


def best_supported_granularity(granularity_review: pd.DataFrame) -> str:
    if granularity_review.empty:
        return "INPUT_MISSING"
    ranked = granularity_review.sort_values(
        ["Interpretable_Profile_Count", "Research_Ready_Profile_Count", "Outcome_Profile_Count"],
        ascending=[False, False, False],
    )
    return str(ranked.iloc[0]["Context_Granularity"])


def _row(granularity: str, group: pd.DataFrame) -> dict[str, object]:
    count = len(group)
    ready = int((group["Outcome_Sample_Adequacy_Class"] == "OUTCOME_RESEARCH_READY_SAMPLE").sum())
    moderate = int((group["Outcome_Sample_Adequacy_Class"] == "MODERATE_OUTCOME_SAMPLE").sum())
    low = int(group["Outcome_Sample_Adequacy_Class"].isin(["LOW_OUTCOME_SAMPLE", "INSUFFICIENT_OUTCOME_SAMPLE"]).sum())
    interpretable = int((group["Outcome_Interpretability_Class"] == "INTERPRETABLE_OUTCOME_PROFILE").sum())
    high_dispersion = int((group["Outcome_Interpretability_Class"] == "NOT_INTERPRETABLE_HIGH_DISPERSION").sum())
    sample_constrained = int((group["Outcome_Interpretability_Class"] == "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED").sum())
    utility_class = _classify(granularity, count, interpretable, moderate, sample_constrained)
    return {
        "Context_Granularity": granularity,
        "Outcome_Profile_Count": count,
        "Research_Ready_Profile_Count": ready,
        "Moderate_Profile_Count": moderate,
        "Low_Or_Insufficient_Profile_Count": low,
        "Interpretable_Profile_Count": interpretable,
        "High_Dispersion_Profile_Count": high_dispersion,
        "Sample_Constrained_Profile_Count": sample_constrained,
        "Context_Granularity_Utility_Class": utility_class,
        "Granularity_Utility_Diagnostic": _diagnostic(utility_class),
    }


def _classify(granularity: str, count: int, interpretable: int, moderate: int, sample_constrained: int) -> str:
    if count == 0:
        return "INPUT_MISSING"
    if sample_constrained > max(interpretable + moderate, 0):
        return "GRANULAR_D1_CONTEXT_SAMPLE_CONSTRAINED"
    if granularity == "H4_TRANSITION_ONLY" and interpretable > 0:
        return "BROAD_CONTEXT_MORE_USEFUL"
    if granularity == "H4_TRANSITION_PLUS_D1_REGIME" and interpretable + moderate > 0:
        return "D1_REGIME_CONTEXT_USEFUL"
    if granularity == "H4_TRANSITION_PLUS_D1_MARKET_STATE" and interpretable + moderate > 0:
        return "D1_MARKET_STATE_CONTEXT_USEFUL"
    return "MIXED_GRANULARITY_UTILITY"


def _diagnostic(utility_class: str) -> str:
    diagnostics = {
        "BROAD_CONTEXT_MORE_USEFUL": "Broader H4 transition context has the strongest descriptive support.",
        "D1_REGIME_CONTEXT_USEFUL": "D1 regime context has descriptive support.",
        "D1_MARKET_STATE_CONTEXT_USEFUL": "D1 market state context has descriptive support.",
        "GRANULAR_D1_CONTEXT_SAMPLE_CONSTRAINED": "Granular D1 context is constrained by sample fragmentation.",
        "MIXED_GRANULARITY_UTILITY": "Granularity utility is mixed across reviewed profiles.",
        "INPUT_MISSING": "Context granularity input is missing.",
    }
    return diagnostics[utility_class]
