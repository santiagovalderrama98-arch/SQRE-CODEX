"""Granularity stability review for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import numeric_series, safe_mean, safe_median, text_series, tier_counts


GRANULARITY_COLUMNS = [
    "Context_Granularity",
    "Reference_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Distinct_Forward_Horizon_Count",
    "Average_Outcome_Sample_Size",
    "Median_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Median_Outcome_Dispersion_Pips",
    "Granularity_Stability_Class",
    "Granularity_Stability_Diagnostic",
]


def build_granularity_stability_review(
    config: ReferenceStabilityValidationConfig, reference_store: pd.DataFrame
) -> pd.DataFrame:
    if reference_store.empty:
        return pd.DataFrame([_missing_row()], columns=GRANULARITY_COLUMNS)
    prepared = reference_store.copy()
    prepared["_granularity"] = text_series(prepared, ["Context_Granularity", "Matched_Context_Granularity"]).replace("", "INPUT_MISSING")
    rows = []
    for granularity, group in prepared.groupby("_granularity", sort=True):
        sample = numeric_series(group, ["Outcome_Sample_Size", "Matched_Outcome_Sample_Size"])
        dispersion = numeric_series(group, ["Outcome_Dispersion_Pips", "Matched_Outcome_Dispersion_Pips"])
        core, supporting, _ = tier_counts(group)
        distinct_horizon = int(numeric_series(group, ["Forward_Horizon_H4_Candles", "Matched_Forward_Horizon_H4_Candles"]).replace(0, pd.NA).dropna().nunique())
        klass = _classify(config, len(group), safe_mean(sample), safe_mean(dispersion), distinct_horizon)
        rows.append(
            {
                "Context_Granularity": granularity,
                "Reference_Count": len(group),
                "Core_Reference_Count": core,
                "Supporting_Reference_Count": supporting,
                "Distinct_Forward_Horizon_Count": distinct_horizon,
                "Average_Outcome_Sample_Size": safe_mean(sample),
                "Median_Outcome_Sample_Size": safe_median(sample),
                "Average_Outcome_Dispersion_Pips": safe_mean(dispersion),
                "Median_Outcome_Dispersion_Pips": safe_median(dispersion),
                "Granularity_Stability_Class": klass,
                "Granularity_Stability_Diagnostic": _diagnostic(klass),
            }
        )
    return pd.DataFrame(rows, columns=GRANULARITY_COLUMNS)


def _classify(
    config: ReferenceStabilityValidationConfig,
    reference_count: int,
    avg_sample: float,
    avg_dispersion: float,
    distinct_horizon: int,
) -> str:
    if reference_count > 0 and avg_sample >= config.minimum_stable_sample_size and avg_dispersion <= config.maximum_stable_dispersion_pips and distinct_horizon:
        return "STABLE_GRANULARITY_CONTEXT"
    if reference_count > 0 and avg_sample >= config.minimum_usable_sample_size and avg_dispersion <= config.maximum_usable_dispersion_pips:
        return "PARTIAL_GRANULARITY_CONTEXT"
    return "FRAGMENTED_GRANULARITY_CONTEXT"


def _diagnostic(klass: str) -> str:
    return {
        "STABLE_GRANULARITY_CONTEXT": "Context granularity has stable descriptive reference evidence.",
        "PARTIAL_GRANULARITY_CONTEXT": "Context granularity has usable but partial descriptive evidence.",
        "FRAGMENTED_GRANULARITY_CONTEXT": "Context granularity is fragmented by sample or dispersion constraints.",
        "INPUT_MISSING": "No context granularity rows were available.",
    }[klass]


def _missing_row() -> dict[str, object]:
    return {
        "Context_Granularity": "INPUT_MISSING",
        "Reference_Count": 0,
        "Core_Reference_Count": 0,
        "Supporting_Reference_Count": 0,
        "Distinct_Forward_Horizon_Count": 0,
        "Average_Outcome_Sample_Size": 0.0,
        "Median_Outcome_Sample_Size": 0.0,
        "Average_Outcome_Dispersion_Pips": 0.0,
        "Median_Outcome_Dispersion_Pips": 0.0,
        "Granularity_Stability_Class": "INPUT_MISSING",
        "Granularity_Stability_Diagnostic": _diagnostic("INPUT_MISSING"),
    }
