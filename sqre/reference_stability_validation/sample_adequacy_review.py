"""Sample adequacy review for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import numeric_series, safe_mean, safe_median, text_series


SAMPLE_COLUMNS = [
    "Review_Group",
    "Reference_Tier",
    "Context_Granularity",
    "Forward_Horizon_H4_Candles",
    "Reference_Count",
    "Stable_Sample_Count",
    "Usable_Sample_Count",
    "Low_Sample_Count",
    "Average_Outcome_Sample_Size",
    "Median_Outcome_Sample_Size",
    "Sample_Adequacy_Class",
    "Sample_Adequacy_Diagnostic",
]


def build_sample_adequacy_review(config: ReferenceStabilityValidationConfig, reference_store: pd.DataFrame) -> pd.DataFrame:
    if reference_store.empty:
        return pd.DataFrame([_missing_row()], columns=SAMPLE_COLUMNS)
    prepared = reference_store.copy()
    prepared["_tier"] = text_series(prepared, ["Reference_Tier", "Matched_Reference_Tier"]).replace("", "INPUT_MISSING")
    prepared["_granularity"] = text_series(prepared, ["Context_Granularity", "Matched_Context_Granularity"]).replace("", "INPUT_MISSING")
    prepared["_horizon"] = numeric_series(prepared, ["Forward_Horizon_H4_Candles", "Matched_Forward_Horizon_H4_Candles"]).astype(int)
    rows = []
    for keys, group in prepared.groupby(["_tier", "_granularity", "_horizon"], sort=True):
        tier, granularity, horizon = keys
        sample = numeric_series(group, ["Outcome_Sample_Size", "Matched_Outcome_Sample_Size"])
        stable = int((sample >= config.minimum_stable_sample_size).sum())
        usable = int(((sample >= config.minimum_usable_sample_size) & (sample < config.minimum_stable_sample_size)).sum())
        low = int((sample < config.minimum_usable_sample_size).sum())
        klass = _classify(stable, usable, low)
        rows.append(
            {
                "Review_Group": f"{tier}|{granularity}|{horizon}",
                "Reference_Tier": tier,
                "Context_Granularity": granularity,
                "Forward_Horizon_H4_Candles": int(horizon),
                "Reference_Count": len(group),
                "Stable_Sample_Count": stable,
                "Usable_Sample_Count": usable,
                "Low_Sample_Count": low,
                "Average_Outcome_Sample_Size": safe_mean(sample),
                "Median_Outcome_Sample_Size": safe_median(sample),
                "Sample_Adequacy_Class": klass,
                "Sample_Adequacy_Diagnostic": _diagnostic(klass),
            }
        )
    return pd.DataFrame(rows, columns=SAMPLE_COLUMNS)


def _classify(stable: int, usable: int, low: int) -> str:
    if stable > 0 and low == 0:
        return "STABLE_SAMPLE_SIZE"
    if stable + usable > low:
        return "USABLE_SAMPLE_SIZE"
    return "LOW_SAMPLE_SIZE"


def _diagnostic(klass: str) -> str:
    return {
        "STABLE_SAMPLE_SIZE": "Reference group has stable sample size for repeated research review.",
        "USABLE_SAMPLE_SIZE": "Reference group has usable but partial sample evidence.",
        "LOW_SAMPLE_SIZE": "Reference group is constrained by low historical sample size.",
        "INPUT_MISSING": "No sample adequacy rows were available.",
    }[klass]


def _missing_row() -> dict[str, object]:
    return {
        "Review_Group": "INPUT_MISSING",
        "Reference_Tier": "INPUT_MISSING",
        "Context_Granularity": "INPUT_MISSING",
        "Forward_Horizon_H4_Candles": 0,
        "Reference_Count": 0,
        "Stable_Sample_Count": 0,
        "Usable_Sample_Count": 0,
        "Low_Sample_Count": 0,
        "Average_Outcome_Sample_Size": 0.0,
        "Median_Outcome_Sample_Size": 0.0,
        "Sample_Adequacy_Class": "INPUT_MISSING",
        "Sample_Adequacy_Diagnostic": _diagnostic("INPUT_MISSING"),
    }
