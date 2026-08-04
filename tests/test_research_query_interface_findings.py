import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.findings import build_summary


def test_findings_marks_ready_when_coverage_and_high_quality_exist():
    requests = pd.DataFrame([{"Research_Query_ID": "RQ_1", "Query_Validation_Status": "VALID_RESEARCH_QUERY"}])
    results = pd.DataFrame(
        [
            {
                "Research_Query_ID": "RQ_1",
                "Research_Query_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
                "Research_Query_Result_Quality_Class": "HIGH_QUALITY_RESEARCH_QUERY_RESULT",
                "Research_Query_Evidence_Class": "CORE_RESEARCH_REFERENCE_EVIDENCE",
                "Matched_Forward_Horizon_H4_Candles": 1,
            }
        ]
    )
    coverage = pd.DataFrame([{"Research_Query_Coverage_Ratio": 1.0}])

    summary = build_summary(pd.DataFrame([{"Research_Reference_ID": "RRS_1"}]), requests, results, coverage, ResearchQueryInterfaceDesignConfig())

    assert summary.research_query_interface_readiness_flag == "READY_FOR_CURRENT_MARKET_STATE_SNAPSHOT_RESEARCH_WORKFLOW"

