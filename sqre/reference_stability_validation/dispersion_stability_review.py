"""Dispersion stability review for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import numeric_series, safe_mean, safe_median, text_series


DISPERSION_COLUMNS = [
    "Review_Group",
    "Reference_Tier",
    "Context_Granularity",
    "Forward_Horizon_H4_Candles",
    "Reference_Count",
    "Stable_Dispersion_Count",
    "Usable_Dispersion_Count",
    "High_Dispersion_Count",
    "Average_Outcome_Dispersion_Pips",
    "Median_Outcome_Dispersion_Pips",
    "Dispersion_Stability_Class",
    "Dispersion_Stability_Diagnostic",
]


def build_dispersion_stability_review(config: ReferenceStabilityValidationConfig, reference_store: pd.DataFrame) -> pd.DataFrame:
    if reference_store.empty:
        return pd.DataFrame([_missing_row()], columns=DISPERSION_COLUMNS)
    prepared = reference_store.copy()
    prepared["_tier"] = text_series(prepared, ["Reference_Tier", "Matched_Reference_Tier"]).replace("", "INPUT_MISSING")
    prepared["_granularity"] = text_series(prepared, ["Context_Granularity", "Matched_Context_Granularity"]).replace("", "INPUT_MISSING")
    prepared["_horizon"] = numeric_series(prepared, ["Forward_Horizon_H4_Candles", "Matched_Forward_Horizon_H4_Candles"]).astype(int)
    rows = []
    for keys, group in prepared.groupby(["_tier", "_granularity", "_horizon"], sort=True):
        tier, granularity, horizon = keys
        dispersion = numeric_series(group, ["Outcome_Dispersion_Pips", "Matched_Outcome_Dispersion_Pips"])
        stable = int((dispersion <= config.maximum_stable_dispersion_pips).sum())
        usable = int(((dispersion > config.maximum_stable_dispersion_pips) & (dispersion <= config.maximum_usable_dispersion_pips)).sum())
        high = int((dispersion > config.maximum_usable_dispersion_pips).sum())
        klass = _classify(stable, usable, high)
        rows.append(
            {
                "Review_Group": f"{tier}|{granularity}|{horizon}",
                "Reference_Tier": tier,
                "Context_Granularity": granularity,
                "Forward_Horizon_H4_Candles": int(horizon),
                "Reference_Count": len(group),
                "Stable_Dispersion_Count": stable,
                "Usable_Dispersion_Count": usable,
                "High_Dispersion_Count": high,
                "Average_Outcome_Dispersion_Pips": safe_mean(dispersion),
                "Median_Outcome_Dispersion_Pips": safe_median(dispersion),
                "Dispersion_Stability_Class": klass,
                "Dispersion_Stability_Diagnostic": _diagnostic(klass),
            }
        )
    return pd.DataFrame(rows, columns=DISPERSION_COLUMNS)


def _classify(stable: int, usable: int, high: int) -> str:
    if stable > 0 and high == 0:
        return "STABLE_DISPERSION"
    if stable + usable > high:
        return "USABLE_DISPERSION"
    return "HIGH_DISPERSION"


def _diagnostic(klass: str) -> str:
    return {
        "STABLE_DISPERSION": "Reference group has stable descriptive dispersion.",
        "USABLE_DISPERSION": "Reference group has usable but wider dispersion.",
        "HIGH_DISPERSION": "Reference group is constrained by high dispersion.",
        "INPUT_MISSING": "No dispersion rows were available.",
    }[klass]


def _missing_row() -> dict[str, object]:
    return {
        "Review_Group": "INPUT_MISSING",
        "Reference_Tier": "INPUT_MISSING",
        "Context_Granularity": "INPUT_MISSING",
        "Forward_Horizon_H4_Candles": 0,
        "Reference_Count": 0,
        "Stable_Dispersion_Count": 0,
        "Usable_Dispersion_Count": 0,
        "High_Dispersion_Count": 0,
        "Average_Outcome_Dispersion_Pips": 0.0,
        "Median_Outcome_Dispersion_Pips": 0.0,
        "Dispersion_Stability_Class": "INPUT_MISSING",
        "Dispersion_Stability_Diagnostic": _diagnostic("INPUT_MISSING"),
    }
