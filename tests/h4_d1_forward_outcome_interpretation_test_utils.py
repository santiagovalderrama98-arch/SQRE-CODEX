"""Test helpers for H4/D1 forward outcome interpretation review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_phase_7515_inputs(base: Path) -> None:
    base.mkdir(parents=True, exist_ok=True)
    profile_rows = [
        _profile("P1", "H4_TRANSITION_ONLY", "RANGE_EXPANSION -> DIRECTIONAL", 1, 25, 0.72, 0.20, 0.08, 12.0, 8.0, -4.0, 16.0),
        _profile("P2", "H4_TRANSITION_ONLY", "RANGE_EXPANSION -> DIRECTIONAL", 2, 24, 0.70, 0.21, 0.09, 13.0, 9.0, -4.0, 18.0),
        _profile("P3", "H4_TRANSITION_ONLY", "RANGE_EXPANSION -> DIRECTIONAL", 3, 23, 0.68, 0.22, 0.10, 10.0, 7.0, -4.0, 17.0),
        _profile("P4", "H4_TRANSITION_PLUS_D1_MARKET_STATE", "DIRECTIONAL -> CONSOLIDATION", 1, 12, 0.20, 0.68, 0.12, -9.0, 3.0, -9.0, 14.0),
        _profile("P5", "H4_TRANSITION_PLUS_D1_REGIME", "CONSOLIDATION -> EXPANSION", 1, 11, 0.45, 0.45, 0.10, 1.0, 6.0, -6.0, 12.0),
        _profile("P6", "H4_TRANSITION_PLUS_D1_STATE_AND_REGIME", "VOLATILE -> ROTATION", 1, 4, 0.50, 0.50, 0.0, 2.0, 4.0, -3.0, 9.0),
        _profile("P7", "H4_TRANSITION_PLUS_D1_STATE_AND_REGIME", "VOLATILE -> ROTATION", 2, 22, 0.40, 0.40, 0.20, 3.0, 30.0, -28.0, 95.0),
    ]
    profiles = pd.DataFrame(profile_rows)
    profiles.to_csv(base / "h4_d1_forward_outcome_profiles.csv", index=False)
    pd.DataFrame({"Forward_Outcome_ID": ["F1"], "Outcome_Completeness_Class": ["COMPLETE_FORWARD_WINDOW"]}).to_csv(
        base / "h4_transition_forward_outcomes.csv",
        index=False,
    )
    pd.DataFrame({"Outcome_Profile_ID": profiles["Outcome_Profile_ID"], "Outcome_Dispersion_Pips": profiles["Outcome_Dispersion_Pips"]}).to_csv(
        base / "h4_d1_forward_outcome_dispersion_review.csv",
        index=False,
    )
    pd.DataFrame({"Outcome_Profile_ID": profiles["Outcome_Profile_ID"], "Outcome_Sample_Adequacy_Class": profiles["Outcome_Sample_Adequacy_Class"]}).to_csv(
        base / "h4_d1_forward_outcome_sample_adequacy_review.csv",
        index=False,
    )
    pd.DataFrame({"Symbol": ["EURUSD"], "Outcome_Profile_Count": [len(profiles)]}).to_csv(
        base / "h4_d1_aligned_forward_outcome_research_summary.csv",
        index=False,
    )


def write_contextual_inputs(base: Path) -> None:
    base.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"Context_Granularity": ["H4_TRANSITION_PLUS_D1_REGIME"], "Profile_Count": [1]}).to_csv(
        base / "h4_d1_same_time_contextual_transition_profiles.csv",
        index=False,
    )
    pd.DataFrame({"Context_Granularity": ["H4_TRANSITION_PLUS_D1_REGIME"], "Sample_Size": [12]}).to_csv(
        base / "h4_d1_context_sample_adequacy_review.csv",
        index=False,
    )
    pd.DataFrame({"Context_Count": [1]}).to_csv(
        base / "h4_d1_same_time_contextual_transition_review_summary.csv",
        index=False,
    )


def _profile(
    profile_id: str,
    granularity: str,
    transition: str,
    horizon: int,
    sample: int,
    up_ratio: float,
    down_ratio: float,
    flat_ratio: float,
    mean_close: float,
    high_excursion: float,
    low_excursion: float,
    dispersion: float,
) -> dict[str, object]:
    return {
        "Outcome_Profile_ID": profile_id,
        "Symbol": "EURUSD",
        "H4_Timeframe": "H4",
        "D1_Timeframe": "D1",
        "Context_Granularity": granularity,
        "H4_Transition_Label": transition,
        "D1_Market_State": "DIRECTIONAL",
        "D1_Regime_Label": "TRENDING",
        "D1_Structure_Direction": "UP",
        "Forward_Horizon_H4_Candles": horizon,
        "Outcome_Sample_Size": sample,
        "Mean_Forward_Close_Change_Pips": mean_close,
        "Median_Forward_Close_Change_Pips": mean_close,
        "Mean_Forward_High_Excursion_Pips": high_excursion,
        "Mean_Forward_Low_Excursion_Pips": low_excursion,
        "Mean_Forward_Range_Pips": abs(high_excursion) + abs(low_excursion),
        "Up_Move_Count": int(round(sample * up_ratio)),
        "Down_Move_Count": int(round(sample * down_ratio)),
        "Flat_Move_Count": max(0, sample - int(round(sample * up_ratio)) - int(round(sample * down_ratio))),
        "Up_Move_Ratio": up_ratio,
        "Down_Move_Ratio": down_ratio,
        "Flat_Move_Ratio": flat_ratio,
        "Outcome_Dispersion_Pips": dispersion,
        "Outcome_Sample_Adequacy_Class": "OUTCOME_RESEARCH_READY_SAMPLE"
        if sample >= 20
        else "MODERATE_OUTCOME_SAMPLE"
        if sample >= 10
        else "LOW_OUTCOME_SAMPLE",
        "Outcome_Profile_Diagnostic": "Synthetic profile.",
    }
