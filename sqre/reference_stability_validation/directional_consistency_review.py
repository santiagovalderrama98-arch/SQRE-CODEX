"""Directional consistency review for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.models import numeric_series, safe_mean, text_series


DIRECTIONAL_COLUMNS = [
    "Review_Group",
    "Context_Granularity",
    "Forward_Horizon_H4_Candles",
    "Directional_Behavior_Class",
    "Dominant_Observed_Direction",
    "Reference_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Directional_Consistency_Class",
    "Directional_Consistency_Diagnostic",
]


def build_directional_consistency_review(reference_store: pd.DataFrame) -> pd.DataFrame:
    if reference_store.empty:
        return pd.DataFrame([_missing_row()], columns=DIRECTIONAL_COLUMNS)
    prepared = reference_store.copy()
    prepared["_granularity"] = text_series(prepared, ["Context_Granularity", "Matched_Context_Granularity"]).replace("", "INPUT_MISSING")
    prepared["_horizon"] = numeric_series(prepared, ["Forward_Horizon_H4_Candles", "Matched_Forward_Horizon_H4_Candles"]).astype(int)
    prepared["_behavior"] = text_series(prepared, ["Directional_Behavior_Class", "Matched_Directional_Behavior_Class"]).replace("", "INPUT_MISSING")
    prepared["_direction"] = text_series(prepared, ["Dominant_Observed_Direction", "Matched_Dominant_Observed_Direction"]).replace("", "INPUT_MISSING")
    rows = []
    for keys, group in prepared.groupby(["_granularity", "_horizon"], sort=True):
        granularity, horizon = keys
        behavior = _mode(group["_behavior"])
        direction = _mode(group["_direction"])
        klass = _classify(group["_behavior"], group["_direction"])
        rows.append(
            {
                "Review_Group": f"{granularity}|{horizon}",
                "Context_Granularity": granularity,
                "Forward_Horizon_H4_Candles": int(horizon),
                "Directional_Behavior_Class": behavior,
                "Dominant_Observed_Direction": direction,
                "Reference_Count": len(group),
                "Average_Outcome_Sample_Size": safe_mean(numeric_series(group, ["Outcome_Sample_Size", "Matched_Outcome_Sample_Size"])),
                "Average_Outcome_Dispersion_Pips": safe_mean(numeric_series(group, ["Outcome_Dispersion_Pips", "Matched_Outcome_Dispersion_Pips"])),
                "Directional_Consistency_Class": klass,
                "Directional_Consistency_Diagnostic": _diagnostic(klass),
            }
        )
    return pd.DataFrame(rows, columns=DIRECTIONAL_COLUMNS)


def _classify(behavior: pd.Series, direction: pd.Series) -> str:
    behavior_values = set(behavior.astype(str).str.upper())
    direction_values = {item for item in direction.astype(str).str.upper() if item not in {"", "INPUT_MISSING", "MIXED"}}
    if any("UNSTABLE" in item for item in behavior_values) or len(direction_values) > 2:
        return "DIRECTIONAL_BEHAVIOR_UNSTABLE"
    if len(direction_values) <= 1 and len(behavior_values) <= 1:
        return "DIRECTIONAL_BEHAVIOR_CONSISTENT"
    return "MIXED_DIRECTIONAL_BEHAVIOR"


def _mode(values: pd.Series) -> str:
    if values.empty:
        return "INPUT_MISSING"
    counts = values.astype(str).str.strip().replace("", "INPUT_MISSING").value_counts()
    return str(counts.index[0]) if len(counts) else "INPUT_MISSING"


def _diagnostic(klass: str) -> str:
    return {
        "DIRECTIONAL_BEHAVIOR_CONSISTENT": "Reference group has consistent descriptive directional behavior.",
        "MIXED_DIRECTIONAL_BEHAVIOR": "Reference group has mixed descriptive directional behavior.",
        "DIRECTIONAL_BEHAVIOR_UNSTABLE": "Reference group has unstable directional behavior diagnostics.",
        "INPUT_MISSING": "No directional consistency rows were available.",
    }[klass]


def _missing_row() -> dict[str, object]:
    return {
        "Review_Group": "INPUT_MISSING",
        "Context_Granularity": "INPUT_MISSING",
        "Forward_Horizon_H4_Candles": 0,
        "Directional_Behavior_Class": "INPUT_MISSING",
        "Dominant_Observed_Direction": "INPUT_MISSING",
        "Reference_Count": 0,
        "Average_Outcome_Sample_Size": 0.0,
        "Average_Outcome_Dispersion_Pips": 0.0,
        "Directional_Consistency_Class": "INPUT_MISSING",
        "Directional_Consistency_Diagnostic": _diagnostic("INPUT_MISSING"),
    }
