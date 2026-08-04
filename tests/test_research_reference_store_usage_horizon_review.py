import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.horizon_usage_review import build_horizon_usage_review


def test_horizon_review_aggregates_by_forward_horizon():
    lookups = pd.DataFrame(
        [
            {
                "Forward_Horizon_H4_Candles": 1,
                "Reference_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_MATCH",
                "Reference_Evidence_Quality_Class": "CORE_REFERENCE_EVIDENCE",
                "Matched_Outcome_Sample_Size": 25,
                "Matched_Outcome_Dispersion_Pips": 20,
            },
            {
                "Forward_Horizon_H4_Candles": 1,
                "Reference_Match_Level": "NO_REFERENCE_MATCH",
                "Reference_Evidence_Quality_Class": "INSUFFICIENT_REFERENCE_EVIDENCE",
                "Matched_Outcome_Sample_Size": 0,
                "Matched_Outcome_Dispersion_Pips": 0,
            },
        ]
    )

    review = build_horizon_usage_review(lookups, ResearchReferenceStoreUsageReviewConfig())

    assert review.iloc[0]["Scenario_Count"] == 2
    assert review.iloc[0]["Matched_Scenario_Count"] == 1
    assert review.iloc[0]["Horizon_Usage_Class"] == "PRIMARY_USAGE_HORIZON"
