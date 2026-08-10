"""Horizon stability review for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import numeric_series, safe_mean, safe_median, text_series, tier_counts


HORIZON_COLUMNS = [
    "Forward_Horizon_H4_Candles",
    "Reference_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Average_Outcome_Sample_Size",
    "Median_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Median_Outcome_Dispersion_Pips",
    "Distinct_Context_Granularity_Count",
    "Horizon_Stability_Class",
    "Horizon_Stability_Diagnostic",
]


def build_horizon_stability_review(config: ReferenceStabilityValidationConfig, reference_store: pd.DataFrame) -> pd.DataFrame:
    if reference_store.empty:
        return pd.DataFrame([_missing_row()], columns=HORIZON_COLUMNS)
    prepared = reference_store.copy()
    prepared["_horizon"] = numeric_series(prepared, ["Forward_Horizon_H4_Candles"]).astype(int)
    rows = []
    for horizon, group in prepared[prepared["_horizon"] > 0].groupby("_horizon", sort=True):
        sample = numeric_series(group, ["Outcome_Sample_Size", "Matched_Outcome_Sample_Size"])
        dispersion = numeric_series(group, ["Outcome_Dispersion_Pips", "Matched_Outcome_Dispersion_Pips"])
        core, supporting, _ = tier_counts(group)
        distinct_granularity = int(text_series(group, ["Context_Granularity", "Matched_Context_Granularity"]).replace("", pd.NA).dropna().nunique())
        klass = _classify(config, safe_mean(sample), safe_mean(dispersion), distinct_granularity)
        rows.append(
            {
                "Forward_Horizon_H4_Candles": int(horizon),
                "Reference_Count": len(group),
                "Core_Reference_Count": core,
                "Supporting_Reference_Count": supporting,
                "Average_Outcome_Sample_Size": safe_mean(sample),
                "Median_Outcome_Sample_Size": safe_median(sample),
                "Average_Outcome_Dispersion_Pips": safe_mean(dispersion),
                "Median_Outcome_Dispersion_Pips": safe_median(dispersion),
                "Distinct_Context_Granularity_Count": distinct_granularity,
                "Horizon_Stability_Class": klass,
                "Horizon_Stability_Diagnostic": _diagnostic(klass),
            }
        )
    return pd.DataFrame(rows or [_missing_row()], columns=HORIZON_COLUMNS)


def _classify(config: ReferenceStabilityValidationConfig, avg_sample: float, avg_dispersion: float, granularity_count: int) -> str:
    if avg_sample >= config.minimum_stable_sample_size and avg_dispersion <= config.maximum_stable_dispersion_pips and granularity_count:
        return "STABLE_ACROSS_HORIZONS"
    if avg_sample >= config.minimum_usable_sample_size and avg_dispersion <= config.maximum_usable_dispersion_pips:
        return "PARTIAL_HORIZON_STABILITY"
    return "HORIZON_UNSTABLE"


def _diagnostic(klass: str) -> str:
    return {
        "STABLE_ACROSS_HORIZONS": "Forward horizon has stable research reference evidence.",
        "PARTIAL_HORIZON_STABILITY": "Forward horizon has usable but partial stability evidence.",
        "HORIZON_UNSTABLE": "Forward horizon remains unstable or constrained for repeated review.",
        "INPUT_MISSING": "No horizon reference rows were available.",
    }[klass]


def _missing_row() -> dict[str, object]:
    return {
        "Forward_Horizon_H4_Candles": 0,
        "Reference_Count": 0,
        "Core_Reference_Count": 0,
        "Supporting_Reference_Count": 0,
        "Average_Outcome_Sample_Size": 0.0,
        "Median_Outcome_Sample_Size": 0.0,
        "Average_Outcome_Dispersion_Pips": 0.0,
        "Median_Outcome_Dispersion_Pips": 0.0,
        "Distinct_Context_Granularity_Count": 0,
        "Horizon_Stability_Class": "INPUT_MISSING",
        "Horizon_Stability_Diagnostic": _diagnostic("INPUT_MISSING"),
    }
