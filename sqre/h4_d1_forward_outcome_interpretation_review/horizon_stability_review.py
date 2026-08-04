"""Horizon stability review for H4/D1 forward outcome interpretations."""

from __future__ import annotations

import pandas as pd


HORIZON_STABILITY_COLUMNS = [
    "Horizon_Stability_ID",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "Profile_Count_Across_Horizons",
    "Covered_Forward_Horizons",
    "Stable_Directional_Behavior_Count",
    "Unstable_Directional_Behavior_Count",
    "Mean_Outcome_Direction_Consistency_Score",
    "Horizon_Stability_Class",
    "Horizon_Stability_Diagnostic",
]

GROUP_COLUMNS = ["Context_Granularity", "H4_Transition_Label", "D1_Market_State", "D1_Regime_Label"]


def build_horizon_stability_review(directional_review: pd.DataFrame) -> pd.DataFrame:
    if directional_review.empty:
        return pd.DataFrame(columns=HORIZON_STABILITY_COLUMNS)
    rows = []
    for sequence, (_, group) in enumerate(directional_review.groupby(GROUP_COLUMNS, dropna=False), start=1):
        rows.append(_row(sequence, group))
    return pd.DataFrame(rows, columns=HORIZON_STABILITY_COLUMNS)


def _row(sequence: int, group: pd.DataFrame) -> dict[str, object]:
    profile_count = len(group)
    horizons = sorted(str(value) for value in group["Forward_Horizon_H4_Candles"].dropna().unique())
    dominant_counts = group["Dominant_Observed_Direction"].value_counts()
    leading_count = int(dominant_counts.max()) if not dominant_counts.empty else 0
    consistency = round(leading_count / profile_count, 6) if profile_count else 0.0
    stable_count = int((group["Dominant_Observed_Direction"] == dominant_counts.index[0]).sum()) if leading_count else 0
    unstable_count = max(0, profile_count - stable_count)
    stability_class = _classify(profile_count, consistency)
    first = group.iloc[0]
    return {
        "Horizon_Stability_ID": f"H4_D1_HORIZON_STABILITY_{sequence:06d}",
        "Context_Granularity": first.get("Context_Granularity", ""),
        "H4_Transition_Label": first.get("H4_Transition_Label", ""),
        "D1_Market_State": first.get("D1_Market_State", ""),
        "D1_Regime_Label": first.get("D1_Regime_Label", ""),
        "Profile_Count_Across_Horizons": profile_count,
        "Covered_Forward_Horizons": "|".join(horizons),
        "Stable_Directional_Behavior_Count": stable_count,
        "Unstable_Directional_Behavior_Count": unstable_count,
        "Mean_Outcome_Direction_Consistency_Score": consistency,
        "Horizon_Stability_Class": stability_class,
        "Horizon_Stability_Diagnostic": _diagnostic(stability_class),
    }


def _classify(profile_count: int, consistency: float) -> str:
    if profile_count < 2:
        return "INSUFFICIENT_HORIZON_COVERAGE"
    if consistency >= 0.80:
        return "STABLE_ACROSS_HORIZONS"
    if consistency >= 0.60:
        return "MODERATELY_STABLE_ACROSS_HORIZONS"
    return "UNSTABLE_ACROSS_HORIZONS"


def _diagnostic(stability_class: str) -> str:
    diagnostics = {
        "STABLE_ACROSS_HORIZONS": "Observed directional behavior is stable across reviewed horizons.",
        "MODERATELY_STABLE_ACROSS_HORIZONS": "Observed directional behavior is moderately stable across horizons.",
        "UNSTABLE_ACROSS_HORIZONS": "Observed directional behavior changes across horizons.",
        "INSUFFICIENT_HORIZON_COVERAGE": "There are too few horizons to review stability.",
        "INPUT_MISSING": "Horizon stability input is missing.",
    }
    return diagnostics[stability_class]
