"""Match level stability review for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import numeric_series, safe_mean, text_series, tier_counts


MATCH_LEVEL_COLUMNS = [
    "Research_Query_Match_Level",
    "Query_Result_Count",
    "Unique_Query_Count",
    "Core_Evidence_Count",
    "Supporting_Evidence_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Match_Level_Stability_Class",
    "Match_Level_Stability_Diagnostic",
]


def build_match_level_stability_review(config: ReferenceStabilityValidationConfig, query_results: pd.DataFrame) -> pd.DataFrame:
    if query_results.empty:
        return pd.DataFrame([_missing_row()], columns=MATCH_LEVEL_COLUMNS)
    prepared = query_results.copy()
    prepared["_match_level"] = text_series(prepared, ["Research_Query_Match_Level", "Snapshot_Query_Match_Level"]).replace("", "INPUT_MISSING")
    rows = []
    for match_level, group in prepared.groupby("_match_level", sort=True):
        sample = numeric_series(group, ["Matched_Outcome_Sample_Size", "Outcome_Sample_Size"])
        dispersion = numeric_series(group, ["Matched_Outcome_Dispersion_Pips", "Outcome_Dispersion_Pips"])
        core, supporting, _ = tier_counts(group, ["Matched_Reference_Tier", "Reference_Tier"])
        klass = _classify(config, str(match_level), safe_mean(sample), safe_mean(dispersion))
        query_id = text_series(group, ["Research_Query_ID", "Snapshot_Query_ID"])
        rows.append(
            {
                "Research_Query_Match_Level": match_level,
                "Query_Result_Count": len(group),
                "Unique_Query_Count": int(query_id.replace("", pd.NA).dropna().nunique()),
                "Core_Evidence_Count": core,
                "Supporting_Evidence_Count": supporting,
                "Average_Outcome_Sample_Size": safe_mean(sample),
                "Average_Outcome_Dispersion_Pips": safe_mean(dispersion),
                "Match_Level_Stability_Class": klass,
                "Match_Level_Stability_Diagnostic": _diagnostic(klass),
            }
        )
    return pd.DataFrame(rows, columns=MATCH_LEVEL_COLUMNS)


def _classify(config: ReferenceStabilityValidationConfig, match_level: str, avg_sample: float, avg_dispersion: float) -> str:
    upper = match_level.upper()
    if "NO_RESEARCH_REFERENCE" in upper or "NO_" in upper or "FALLBACK" in upper or "BROADER" in upper:
        return "FALLBACK_DEPENDENT_MATCH_USAGE"
    if avg_sample >= config.minimum_stable_sample_size and avg_dispersion <= config.maximum_stable_dispersion_pips:
        return "STABLE_MATCH_LEVEL_USAGE"
    if avg_sample >= config.minimum_usable_sample_size and avg_dispersion <= config.maximum_usable_dispersion_pips:
        return "PARTIAL_MATCH_LEVEL_USAGE"
    return "FALLBACK_DEPENDENT_MATCH_USAGE"


def _diagnostic(klass: str) -> str:
    return {
        "STABLE_MATCH_LEVEL_USAGE": "Match level has stable descriptive reference usage.",
        "PARTIAL_MATCH_LEVEL_USAGE": "Match level has usable but partial descriptive reference usage.",
        "FALLBACK_DEPENDENT_MATCH_USAGE": "Match level relies on broader fallback or limited reference usage.",
        "INPUT_MISSING": "No match level rows were available.",
    }[klass]


def _missing_row() -> dict[str, object]:
    return {
        "Research_Query_Match_Level": "INPUT_MISSING",
        "Query_Result_Count": 0,
        "Unique_Query_Count": 0,
        "Core_Evidence_Count": 0,
        "Supporting_Evidence_Count": 0,
        "Average_Outcome_Sample_Size": 0.0,
        "Average_Outcome_Dispersion_Pips": 0.0,
        "Match_Level_Stability_Class": "INPUT_MISSING",
        "Match_Level_Stability_Diagnostic": _diagnostic("INPUT_MISSING"),
    }
