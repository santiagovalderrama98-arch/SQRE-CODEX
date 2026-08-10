import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.findings import build_summary


def test_findings_produce_ready_flag_for_usable_snapshot_references():
    frames = {
        "snapshot_research_summary": pd.DataFrame(
            [
                {
                    "Research_Reference_Count": 213,
                    "Snapshot_Query_Count": 5,
                    "Snapshot_Result_Count": 10,
                    "Snapshot_Reference_Coverage_Ratio": 1.0,
                    "Current_Market_State_Snapshot_Readiness_Flag": "READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE",
                }
            ]
        ),
        "snapshot_context": pd.DataFrame([{"Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT"}]),
        "reference_store": pd.DataFrame([{"Research_Reference_ID": "R1"}]),
    }

    summary = build_summary(
        frames,
        [],
        pd.DataFrame([{"Reference_Card_ID": "REF_CARD_000001"}]),
        pd.DataFrame([{"Snapshot_Evidence_Class": "CORE"}]),
        pd.DataFrame([{"Snapshot_ID": "S1"}]),
        pd.DataFrame([{"Snapshot_Query_ID": "Q1"}]),
        pd.DataFrame([{"Diagnostic_Category": "SNAPSHOT_CONTEXT"}]),
        ResearchDashboardPrototypeConfig(),
    )

    assert summary.dashboard_readiness_class == "RESEARCH_DASHBOARD_PROTOTYPE_READY"
    assert summary.dashboard_readiness_flag == "READY_FOR_MANUAL_RESEARCH_REVIEW"


def test_findings_produce_input_completeness_flag_when_required_inputs_missing():
    summary = build_summary(
        {},
        [],
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        ResearchDashboardPrototypeConfig(),
    )

    assert summary.dashboard_readiness_class == "INPUT_MISSING"
    assert summary.dashboard_readiness_flag == "INPUT_COMPLETENESS_REVIEW_REQUIRED"
