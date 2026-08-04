from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_contextual_transition_inputs(path: Path) -> pd.DataFrame:
    path.mkdir(parents=True, exist_ok=True)
    profiles = pd.DataFrame(
        [
            _profile("CTX_1", "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT", "D1_TREND", "D1_EXPANSION", "UP", 14, 40, "RESEARCH_READY_CONTEXT_SAMPLE"),
            _profile("CTX_2", "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT", "D1_RANGE", "D1_ROTATION", "DOWN", 4, 40, "LOW_CONTEXT_SAMPLE"),
            _profile("CTX_3", "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT", "D1_RANGE", "D1_BALANCED", "DOWN", 3, 40, "LOW_CONTEXT_SAMPLE"),
            _profile("CTX_4", "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT", "D1_RANGE", "D1_BALANCED", "FLAT", 2, 40, "INSUFFICIENT_CONTEXT_SAMPLE"),
            _profile("CTX_5", "DIRECTIONAL_DISPLACEMENT -> RANGE_CONTRACTION", "D1_TREND", "D1_EXPANSION", "UP", 12, 18, "RESEARCH_READY_CONTEXT_SAMPLE"),
        ]
    )
    profiles.to_csv(path / "h4_d1_same_time_contextual_transition_profiles.csv", index=False)
    pd.DataFrame(
        [
            {
                "H4_Transition_Label": "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT",
                "D1_Market_State": "D1_RANGE",
                "Context_Row_Count": 9,
            }
        ]
    ).to_csv(path / "h4_transition_d1_market_state_distribution.csv", index=False)
    pd.DataFrame(
        [
            {
                "H4_Transition_Label": "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT",
                "D1_Regime_Label": "D1_BALANCED",
                "Context_Row_Count": 5,
            }
        ]
    ).to_csv(path / "h4_transition_d1_regime_distribution.csv", index=False)
    pd.DataFrame(
        [
            {
                "H4_Transition_Label": "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT",
                "Dominant_D1_Market_State": "D1_RANGE",
                "Dominant_D1_Market_State_Share": 0.64,
                "Dominant_D1_Regime_Label": "D1_BALANCED",
                "Dominant_D1_Regime_Share": 0.36,
            }
        ]
    ).to_csv(path / "h4_transition_context_concentration_review.csv", index=False)
    pd.DataFrame(
        [
            {
                "Context_Profile_ID": "CTX_1",
                "Context_Sample_Adequacy_Class": "RESEARCH_READY_CONTEXT_SAMPLE",
            }
        ]
    ).to_csv(path / "h4_d1_context_sample_adequacy_review.csv", index=False)
    pd.DataFrame(
        [
            {
                "Context_Profile_Count": len(profiles),
                "Research_Ready_Context_Count": 2,
                "Low_Or_Insufficient_Context_Count": 3,
            }
        ]
    ).to_csv(path / "h4_d1_same_time_contextual_transition_review_summary.csv", index=False)
    return profiles


def write_optional_supporting_inputs(alignment_dir: Path, timestamped_dir: Path) -> None:
    alignment_dir.mkdir(parents=True, exist_ok=True)
    timestamped_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"Rows": [1]}).to_csv(alignment_dir / "h4_transition_d1_same_time_alignment.csv", index=False)
    pd.DataFrame({"Rows": [1]}).to_csv(alignment_dir / "h4_state_d1_same_time_alignment.csv", index=False)
    pd.DataFrame({"Rows": [1]}).to_csv(alignment_dir / "h4_d1_same_time_alignment_summary.csv", index=False)
    pd.DataFrame({"Rows": [1]}).to_csv(timestamped_dir / "timestamped_d1_market_states.csv", index=False)
    pd.DataFrame({"Rows": [1]}).to_csv(timestamped_dir / "timestamped_h4_d1_state_regime_summary.csv", index=False)


def _profile(
    context_id: str,
    transition: str,
    market_state: str,
    regime: str,
    direction: str,
    rows: int,
    transition_total: int,
    adequacy_class: str,
) -> dict[str, object]:
    return {
        "Context_Profile_ID": context_id,
        "H4_Transition_Label": transition,
        "D1_Market_State": market_state,
        "D1_Regime_Label": regime,
        "D1_Structure_Direction": direction,
        "Context_Row_Count": rows,
        "Transition_Total_Count": transition_total,
        "Context_Sample_Adequacy_Class": adequacy_class,
        "Contextual_Review_Class": "SAME_TIME_CONTEXT_RESEARCH_READY"
        if adequacy_class == "RESEARCH_READY_CONTEXT_SAMPLE"
        else "SAME_TIME_CONTEXT_SAMPLE_CONSTRAINED",
    }
