import pandas as pd

from sqre.research_reference_store_design.granularity_reference_review import build_granularity_reference_review


def test_granularity_review_identifies_primary_reference_granularity():
    candidates = pd.DataFrame(
        [
            _row("H4_TRANSITION_ONLY", "CORE_RESEARCH_REFERENCE", "INCLUDED_IN_RESEARCH_REFERENCE_STORE"),
            _row("H4_TRANSITION_ONLY", "SUPPORTING_RESEARCH_REFERENCE", "INCLUDED_IN_RESEARCH_REFERENCE_STORE"),
            _row("D1_STATE", "EXCLUDED_SAMPLE_CONSTRAINED", "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE"),
        ]
    )

    review = build_granularity_reference_review(candidates)

    assert review.iloc[0]["Context_Granularity"] == "H4_TRANSITION_ONLY"
    assert review.iloc[0]["Granularity_Reference_Utility_Class"] == "PRIMARY_REFERENCE_GRANULARITY"


def _row(granularity: str, tier: str, status: str) -> dict[str, str]:
    return {"Context_Granularity": granularity, "Reference_Tier": tier, "Reference_Inclusion_Status": status}
