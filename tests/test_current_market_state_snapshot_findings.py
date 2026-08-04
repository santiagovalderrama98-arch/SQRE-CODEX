import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.findings import build_summary


def test_findings_summary_marks_dashboard_ready_when_evidence_exists():
    summary = build_summary(
        pd.DataFrame([{"Research_Reference_ID": "R1"}]),
        pd.DataFrame([{"Snapshot_Mode": "USER_SUPPLIED_SNAPSHOT", "Snapshot_Source": "USER", "Snapshot_Validation_Status": "VALID"}]),
        pd.DataFrame([{"Snapshot_Query_ID": "Q1"}]),
        pd.DataFrame(
            [
                {
                    "Snapshot_Query_ID": "Q1",
                    "Matched_Research_Reference_ID": "R1",
                    "Snapshot_Research_Result_Class": "HIGH_EVIDENCE_SNAPSHOT_REFERENCE",
                    "Snapshot_Evidence_Class": "CORE_SNAPSHOT_REFERENCE_EVIDENCE",
                    "Snapshot_Query_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
                    "Matched_Forward_Horizon_H4_Candles": 1,
                }
            ]
        ),
        CurrentMarketStateSnapshotResearchConfig(),
    )

    assert summary.current_market_state_snapshot_readiness_flag == "READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE"
    assert summary.snapshot_reference_coverage_ratio == 1.0
