"""Reference horizon usage review."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig


HORIZON_USAGE_COLUMNS = [
    "Forward_Horizon_H4_Candles",
    "Scenario_Count",
    "Matched_Scenario_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Horizon_Usage_Class",
    "Horizon_Usage_Diagnostic",
]


def build_horizon_usage_review(
    lookup_results: pd.DataFrame,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> pd.DataFrame:
    if lookup_results.empty or bool((lookup_results["Reference_Match_Level"] == "INPUT_MISSING").all()):
        return pd.DataFrame([_empty("INPUT_MISSING", "Required usage inputs are missing.")], columns=HORIZON_USAGE_COLUMNS)
    rows = [_row(horizon, group, config) for horizon, group in lookup_results.groupby("Forward_Horizon_H4_Candles", sort=True)]
    return pd.DataFrame(rows, columns=HORIZON_USAGE_COLUMNS)


def _row(horizon: object, group: pd.DataFrame, config: ResearchReferenceStoreUsageReviewConfig) -> dict[str, object]:
    matched = group[~group["Reference_Match_Level"].isin(["NO_REFERENCE_MATCH", "INPUT_MISSING"])]
    sample = pd.to_numeric(matched["Matched_Outcome_Sample_Size"], errors="coerce").fillna(0)
    dispersion = pd.to_numeric(matched["Matched_Outcome_Dispersion_Pips"], errors="coerce").fillna(0)
    core = int((matched["Reference_Evidence_Quality_Class"] == "CORE_REFERENCE_EVIDENCE").sum())
    supporting = int((matched["Reference_Evidence_Quality_Class"] == "SUPPORTING_REFERENCE_EVIDENCE").sum())
    avg_sample = float(sample.mean()) if not sample.empty else 0.0
    return {
        "Forward_Horizon_H4_Candles": horizon,
        "Scenario_Count": len(group),
        "Matched_Scenario_Count": len(matched),
        "Core_Reference_Count": core,
        "Supporting_Reference_Count": supporting,
        "Average_Outcome_Sample_Size": round(avg_sample, 4),
        "Average_Outcome_Dispersion_Pips": round(float(dispersion.mean()), 4) if not dispersion.empty else 0.0,
        "Horizon_Usage_Class": _classify(len(matched), core, supporting, avg_sample, config),
        "Horizon_Usage_Diagnostic": f"Horizon {horizon} produced {len(matched)} descriptive reference matches.",
    }


def _classify(matched: int, core: int, supporting: int, avg_sample: float, config: ResearchReferenceStoreUsageReviewConfig) -> str:
    if matched == 0:
        return "SAMPLE_CONSTRAINED_USAGE_HORIZON"
    if core > 0:
        return "PRIMARY_USAGE_HORIZON"
    if supporting > 0 and avg_sample >= config.minimum_reference_sample_size:
        return "SUPPORTING_USAGE_HORIZON"
    return "LIMITED_USAGE_HORIZON"


def _empty(horizon: object, diagnostic: str) -> dict[str, object]:
    return {
        "Forward_Horizon_H4_Candles": horizon,
        "Scenario_Count": 0,
        "Matched_Scenario_Count": 0,
        "Core_Reference_Count": 0,
        "Supporting_Reference_Count": 0,
        "Average_Outcome_Sample_Size": 0.0,
        "Average_Outcome_Dispersion_Pips": 0.0,
        "Horizon_Usage_Class": "INPUT_MISSING",
        "Horizon_Usage_Diagnostic": diagnostic,
    }
