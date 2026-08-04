import pandas as pd

from sqre.research_reference_store_design.reference_exclusion_review import build_reference_exclusion_review


def test_exclusion_review_explains_excluded_profiles():
    candidates = pd.DataFrame(
        [
            {
                "Research_Reference_Candidate_ID": "RRC_1",
                "Outcome_Profile_ID": "OP_1",
                "Context_Granularity": "H4_TRANSITION_ONLY",
                "H4_Transition_Label": "A",
                "D1_Market_State": "",
                "D1_Regime_Label": "",
                "Forward_Horizon_H4_Candles": 3,
                "Outcome_Sample_Size": 5,
                "Outcome_Dispersion_Pips": 10,
                "Outcome_Interpretability_Class": "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED",
                "Reference_Tier": "EXCLUDED_SAMPLE_CONSTRAINED",
                "Reference_Inclusion_Status": "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE",
            }
        ]
    )

    review = build_reference_exclusion_review(candidates)

    assert review.iloc[0]["Exclusion_Reason_Class"] == "SAMPLE_CONSTRAINED"
    assert review.iloc[0]["Recommended_Follow_Up"] == "EXPAND_HISTORICAL_SAMPLE"


def test_exclusion_review_explains_horizon_watchlist_profiles():
    candidates = pd.DataFrame(
        [
            {
                "Research_Reference_Candidate_ID": "RRC_1",
                "Outcome_Profile_ID": "OP_1",
                "Reference_Tier": "WATCHLIST_RESEARCH_REFERENCE",
                "Reference_Inclusion_Status": "WATCHLIST_ONLY",
                "Reference_Diagnostic": "Profile is retained for review due to horizon instability.",
            }
        ]
    )

    review = build_reference_exclusion_review(candidates)

    assert review.iloc[0]["Exclusion_Reason_Class"] == "UNSTABLE_HORIZON_CONTEXT"
