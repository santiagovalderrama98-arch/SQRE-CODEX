"""Build forward outcome profiles across context granularities."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.context_granularity_profiler import CONTEXT_GRANULARITIES


OUTCOME_PROFILE_COLUMNS = [
    "Outcome_Profile_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Forward_Horizon_H4_Candles",
    "Outcome_Sample_Size",
    "Mean_Forward_Close_Change_Pips",
    "Median_Forward_Close_Change_Pips",
    "Mean_Forward_High_Excursion_Pips",
    "Mean_Forward_Low_Excursion_Pips",
    "Mean_Forward_Range_Pips",
    "Up_Move_Count",
    "Down_Move_Count",
    "Flat_Move_Count",
    "Up_Move_Ratio",
    "Down_Move_Ratio",
    "Flat_Move_Ratio",
    "Outcome_Dispersion_Pips",
    "Outcome_Sample_Adequacy_Class",
    "Outcome_Profile_Diagnostic",
]


def build_outcome_profiles(
    forward_outcomes: pd.DataFrame,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> pd.DataFrame:
    if forward_outcomes.empty:
        return pd.DataFrame(columns=OUTCOME_PROFILE_COLUMNS)
    complete_or_partial = forward_outcomes[
        forward_outcomes["Outcome_Completeness_Class"].isin(["COMPLETE_FORWARD_WINDOW", "PARTIAL_FORWARD_WINDOW"])
    ].copy()
    if complete_or_partial.empty:
        return pd.DataFrame(columns=OUTCOME_PROFILE_COLUMNS)
    rows = []
    sequence = 1
    for granularity, columns in CONTEXT_GRANULARITIES.items():
        group_columns = columns + ["Forward_Horizon_H4_Candles"]
        for _, group in complete_or_partial.groupby(group_columns, dropna=False):
            rows.append(_profile_row(sequence, granularity, group, config))
            sequence += 1
    return pd.DataFrame(rows, columns=OUTCOME_PROFILE_COLUMNS)


def classify_outcome_sample_adequacy(
    sample_size: int,
    granularity: str,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> str:
    minimum = _minimum_for_granularity(granularity, config)
    if sample_size >= minimum:
        return "OUTCOME_RESEARCH_READY_SAMPLE"
    if sample_size >= max(1, minimum // 2):
        return "MODERATE_OUTCOME_SAMPLE"
    if sample_size > 0:
        return "LOW_OUTCOME_SAMPLE"
    return "INSUFFICIENT_OUTCOME_SAMPLE"


def minimum_sample_size_for_profile(
    granularity: str,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> int:
    return _minimum_for_granularity(granularity, config)


def _profile_row(
    sequence: int,
    granularity: str,
    group: pd.DataFrame,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> dict[str, object]:
    sample_size = len(group)
    adequacy_class = classify_outcome_sample_adequacy(sample_size, granularity, config)
    up_count = int((group["Directional_Follow_Through_Class"] == "FORWARD_UP_MOVE").sum())
    down_count = int((group["Directional_Follow_Through_Class"] == "FORWARD_DOWN_MOVE").sum())
    flat_count = int((group["Directional_Follow_Through_Class"] == "FORWARD_FLAT_MOVE").sum())
    return {
        "Outcome_Profile_ID": f"H4_D1_OUTCOME_PROFILE_{sequence:06d}",
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "Context_Granularity": granularity,
        "H4_Transition_Label": _first(group, "H4_Transition_Label"),
        "D1_Market_State": _first(group, "D1_Market_State") if "D1_Market_State" in group else "",
        "D1_Regime_Label": _first(group, "D1_Regime_Label") if "D1_Regime_Label" in group else "",
        "D1_Structure_Direction": _first(group, "D1_Structure_Direction") if "D1_Structure_Direction" in group else "",
        "Forward_Horizon_H4_Candles": int(_first(group, "Forward_Horizon_H4_Candles")),
        "Outcome_Sample_Size": sample_size,
        "Mean_Forward_Close_Change_Pips": _mean(group, "Forward_Close_Change_Pips"),
        "Median_Forward_Close_Change_Pips": _median(group, "Forward_Close_Change_Pips"),
        "Mean_Forward_High_Excursion_Pips": _mean(group, "Forward_High_Excursion_Pips"),
        "Mean_Forward_Low_Excursion_Pips": _mean(group, "Forward_Low_Excursion_Pips"),
        "Mean_Forward_Range_Pips": _mean(group, "Forward_Range_Pips"),
        "Up_Move_Count": up_count,
        "Down_Move_Count": down_count,
        "Flat_Move_Count": flat_count,
        "Up_Move_Ratio": _ratio(up_count, sample_size),
        "Down_Move_Ratio": _ratio(down_count, sample_size),
        "Flat_Move_Ratio": _ratio(flat_count, sample_size),
        "Outcome_Dispersion_Pips": _dispersion(group, "Forward_Close_Change_Pips"),
        "Outcome_Sample_Adequacy_Class": adequacy_class,
        "Outcome_Profile_Diagnostic": _diagnostic(adequacy_class),
    }


def _minimum_for_granularity(granularity: str, config: H4D1AlignedForwardOutcomeResearchConfig) -> int:
    if granularity == "H4_TRANSITION_ONLY":
        return config.minimum_outcome_sample_size
    return config.minimum_context_outcome_sample_size


def _first(group: pd.DataFrame, column: str) -> object:
    return group.iloc[0][column]


def _mean(group: pd.DataFrame, column: str) -> float:
    return round(float(pd.to_numeric(group[column], errors="coerce").mean()), 6)


def _median(group: pd.DataFrame, column: str) -> float:
    return round(float(pd.to_numeric(group[column], errors="coerce").median()), 6)


def _dispersion(group: pd.DataFrame, column: str) -> float:
    return round(float(pd.to_numeric(group[column], errors="coerce").std(ddof=0)), 6)


def _ratio(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def _diagnostic(adequacy_class: str) -> str:
    if adequacy_class == "OUTCOME_RESEARCH_READY_SAMPLE":
        return "Outcome profile has enough observations for later interpretation review."
    if adequacy_class == "MODERATE_OUTCOME_SAMPLE":
        return "Outcome profile has moderate descriptive sample depth."
    if adequacy_class == "LOW_OUTCOME_SAMPLE":
        return "Outcome profile sample is low."
    return "Outcome profile sample is insufficient."
