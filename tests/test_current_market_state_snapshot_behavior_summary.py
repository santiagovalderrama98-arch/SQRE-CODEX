import pandas as pd

from sqre.current_market_state_snapshot_research.snapshot_behavior_summary import build_snapshot_behavior_summary


def test_behavior_summary_is_descriptive():
    queries = pd.DataFrame([{"Snapshot_ID": "CMS_1", "Snapshot_Query_ID": "Q1"}])
    results = pd.DataFrame(
        [
            {
                "Snapshot_Query_ID": "Q1",
                "Matched_Research_Reference_ID": "R1",
                "Matched_Forward_Horizon_H4_Candles": 1,
                "Snapshot_Query_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
                "Snapshot_Evidence_Class": "CORE_SNAPSHOT_REFERENCE_EVIDENCE",
                "Snapshot_Research_Result_Class": "HIGH_EVIDENCE_SNAPSHOT_REFERENCE",
                "Matched_Directional_Behavior_Class": "MIXED",
                "Matched_Dominant_Observed_Direction": "UP",
            }
        ]
    )

    summary = build_snapshot_behavior_summary(queries, results)

    assert summary.iloc[0]["Snapshot_Result_Count"] == 1
    assert "descriptive historical references" in summary.iloc[0]["Behavior_Summary_Diagnostic"]
