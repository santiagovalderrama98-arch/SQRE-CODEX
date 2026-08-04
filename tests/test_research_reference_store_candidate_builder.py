import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.reference_candidate_builder import build_reference_candidates


def test_candidate_builder_joins_interpretability_directional_excursion_and_horizon():
    interpretability = pd.DataFrame(
        [
            {
                "Outcome_Profile_ID": "OP_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "Context_Granularity": "H4_TRANSITION_ONLY",
                "H4_Transition_Label": "RANGE_EXPANSION",
                "D1_Market_State": "",
                "D1_Regime_Label": "",
                "D1_Structure_Direction": "",
                "Forward_Horizon_H4_Candles": 3,
                "Outcome_Sample_Size": 30,
                "Mean_Forward_Close_Change_Pips": 2.5,
                "Median_Forward_Close_Change_Pips": 1.2,
                "Outcome_Dispersion_Pips": 20,
                "Outcome_Sample_Adequacy_Class": "ADEQUATE_SAMPLE",
                "Outcome_Interpretability_Class": "INTERPRETABLE_OUTCOME_PROFILE",
            }
        ]
    )
    directional = pd.DataFrame(
        [{"Outcome_Profile_ID": "OP_1", "Directional_Behavior_Class": "OBSERVED_MIXED_DIRECTIONAL_BEHAVIOR", "Dominant_Observed_Direction": "OBSERVED_MIXED"}]
    )
    excursion = pd.DataFrame([{"Outcome_Profile_ID": "OP_1", "Excursion_Behavior_Class": "BALANCED_EXCURSION_BEHAVIOR"}])
    horizon = pd.DataFrame(
        [
            {
                "Context_Granularity": "H4_TRANSITION_ONLY",
                "H4_Transition_Label": "RANGE_EXPANSION",
                "D1_Market_State": "",
                "D1_Regime_Label": "",
                "Horizon_Stability_Class": "STABLE_ACROSS_HORIZONS",
            }
        ]
    )

    candidates = build_reference_candidates(interpretability, directional, excursion, horizon, ResearchReferenceStoreDesignConfig())

    row = candidates.iloc[0]
    assert row["Reference_Tier"] == "CORE_RESEARCH_REFERENCE"
    assert row["Directional_Behavior_Class"] == "OBSERVED_MIXED_DIRECTIONAL_BEHAVIOR"
    assert row["Excursion_Behavior_Class"] == "BALANCED_EXCURSION_BEHAVIOR"
    assert row["Horizon_Stability_Class"] == "STABLE_ACROSS_HORIZONS"
