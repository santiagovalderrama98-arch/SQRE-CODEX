import pandas as pd

from sqre.current_market_state_snapshot_research.snapshot_evidence_review import build_snapshot_evidence_review


def test_evidence_review_aggregates_result_classes():
    frame = pd.DataFrame(
        [
            {
                "Snapshot_Query_ID": "Q1",
                "Snapshot_Evidence_Class": "CORE_SNAPSHOT_REFERENCE_EVIDENCE",
                "Matched_Reference_Tier": "CORE_REFERENCE",
                "Matched_Outcome_Sample_Size": 30,
                "Matched_Outcome_Dispersion_Pips": 20,
            }
        ]
    )

    review = build_snapshot_evidence_review(frame)

    assert review.iloc[0]["Snapshot_Result_Count"] == 1
    assert review.iloc[0]["Core_Reference_Count"] == 1
