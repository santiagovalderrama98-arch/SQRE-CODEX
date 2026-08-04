import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.reference_availability_review import build_reference_availability_review


def test_availability_review_counts_match_levels():
    lookups = pd.DataFrame(
        [
            {"Reference_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_MATCH"},
            {"Reference_Match_Level": "D1_REGIME_CONTEXT_MATCH"},
            {"Reference_Match_Level": "NO_REFERENCE_MATCH"},
        ]
    )

    review = build_reference_availability_review(lookups, ResearchReferenceStoreUsageReviewConfig())

    assert review.iloc[0]["Usage_Scenario_Count"] == 3
    assert review.iloc[0]["Matched_Scenario_Count"] == 2
    assert review.iloc[0]["Reference_Availability_Ratio"] == 0.6667


def test_availability_review_handles_input_missing():
    lookups = pd.DataFrame([{"Reference_Match_Level": "INPUT_MISSING"}])

    review = build_reference_availability_review(lookups, ResearchReferenceStoreUsageReviewConfig())

    assert review.iloc[0]["Reference_Availability_Class"] == "INPUT_MISSING"
