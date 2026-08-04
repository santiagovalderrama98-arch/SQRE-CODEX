import pandas as pd

from sqre.research_reference_store_usage_review.evidence_quality_review import build_evidence_quality_review


def test_evidence_quality_review_groups_lookup_rows():
    lookups = pd.DataFrame(
        [
            {
                "Reference_Evidence_Quality_Class": "CORE_REFERENCE_EVIDENCE",
                "Matched_Outcome_Sample_Size": 25,
                "Matched_Outcome_Dispersion_Pips": 20,
            },
            {
                "Reference_Evidence_Quality_Class": "SUPPORTING_REFERENCE_EVIDENCE",
                "Matched_Outcome_Sample_Size": 12,
                "Matched_Outcome_Dispersion_Pips": 40,
            },
        ]
    )

    review = build_evidence_quality_review(lookups)

    assert set(review["Reference_Evidence_Quality_Class"]) == {
        "CORE_REFERENCE_EVIDENCE",
        "SUPPORTING_REFERENCE_EVIDENCE",
    }
