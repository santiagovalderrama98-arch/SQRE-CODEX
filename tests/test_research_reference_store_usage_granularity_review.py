import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.granularity_usage_review import build_granularity_usage_review


def test_granularity_review_marks_exact_core_as_primary():
    lookups = pd.DataFrame(
        [
            {
                "Reference_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_MATCH",
                "Reference_Evidence_Quality_Class": "CORE_REFERENCE_EVIDENCE",
                "Matched_Outcome_Sample_Size": 25,
                "Matched_Outcome_Dispersion_Pips": 20,
            }
        ]
    )

    review = build_granularity_usage_review(lookups, ResearchReferenceStoreUsageReviewConfig())

    assert review.iloc[0]["Granularity_Usage_Class"] == "PRIMARY_USAGE_GRANULARITY"
