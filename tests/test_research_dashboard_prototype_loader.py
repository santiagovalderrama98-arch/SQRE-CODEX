from pathlib import Path

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.loader import ResearchDashboardPrototypeLoader


def test_loader_handles_missing_required_inputs_safely(tmp_path):
    config = ResearchDashboardPrototypeConfig(snapshot_research_dir=tmp_path / "missing")

    frames = ResearchDashboardPrototypeLoader(config).load_inputs()

    assert "snapshot_context" in frames
    assert frames["snapshot_context"].empty


def test_loader_loads_snapshot_research_outputs(tmp_path):
    snapshot_dir = tmp_path / "snapshot"
    snapshot_dir.mkdir()
    pd.DataFrame([{"Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT"}]).to_csv(
        snapshot_dir / "current_market_state_snapshot_context.csv", index=False
    )
    config = ResearchDashboardPrototypeConfig(snapshot_research_dir=snapshot_dir)

    frames = ResearchDashboardPrototypeLoader(config).load_inputs()

    assert frames["snapshot_context"].iloc[0]["Snapshot_Mode"] == "LATEST_AVAILABLE_SNAPSHOT"


def write_minimal_snapshot_inputs(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"Source_Name": "snapshot_context"}]).to_csv(
        directory / "current_market_state_snapshot_source_inventory.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT",
                "Snapshot_Source": "SAME_TIME_ALIGNMENT_LATEST_ROW",
                "Snapshot_Timestamp": "2026-07-03 20:00:00",
                "Snapshot_Timestamp_Status": "LATEST_AVAILABLE",
                "Snapshot_Validation_Status": "VALID_SNAPSHOT_CONTEXT",
                "H4_Transition_Label": "A_TO_B",
                "H4_Market_State": "EXPANSION",
                "D1_Market_State": "CONSOLIDATION",
                "D1_Regime_Label": "REGIME_A",
                "D1_Structure_Direction": "UP",
            }
        ]
    ).to_csv(directory / "current_market_state_snapshot_context.csv", index=False)
    pd.DataFrame([{"Snapshot_Query_ID": "Q1", "Requested_Forward_Horizon_H4_Candles": 1}]).to_csv(
        directory / "current_market_state_snapshot_query_requests.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "Snapshot_Query_ID": "Q1",
                "Requested_Forward_Horizon_H4_Candles": 1,
                "Matched_Research_Reference_ID": "R1",
                "Matched_Outcome_Profile_ID": "OP1",
                "Matched_Context_Granularity": "D1_REGIME_CONTEXT",
                "Matched_Reference_Tier": "CORE_REFERENCE",
                "Matched_Forward_Horizon_H4_Candles": 1,
                "Matched_Outcome_Sample_Size": 44,
                "Matched_Outcome_Dispersion_Pips": 12.5,
                "Matched_Mean_Forward_Close_Change_Pips": 1.2,
                "Matched_Median_Forward_Close_Change_Pips": 0.8,
                "Matched_Directional_Behavior_Class": "DIRECTIONAL",
                "Matched_Dominant_Observed_Direction": "UP",
                "Matched_Excursion_Behavior_Class": "BALANCED",
                "Matched_Horizon_Stability_Class": "STABLE",
                "Snapshot_Query_Match_Level": "D1_REGIME_CONTEXT_QUERY_MATCH",
                "Snapshot_Research_Result_Class": "HIGH_EVIDENCE_SNAPSHOT_REFERENCE",
                "Snapshot_Evidence_Class": "CORE_SNAPSHOT_REFERENCE_EVIDENCE",
                "Result_Rank": 1,
            }
        ]
    ).to_csv(directory / "current_market_state_snapshot_reference_results.csv", index=False)
    pd.DataFrame(
        [
            {
                "Snapshot_Query_ID": "Q1",
                "Fallback_Attempt_Order": 1,
                "Attempted_Match_Level": "D1_REGIME_CONTEXT_QUERY_MATCH",
                "Attempted_H4_Transition_Label": "A_TO_B",
                "Attempted_D1_Market_State": "CONSOLIDATION",
                "Attempted_D1_Regime_Label": "REGIME_A",
                "Attempted_Forward_Horizon_H4_Candles": 1,
                "Candidate_Reference_Count": 2,
                "Selected_Result_Count": 1,
                "Fallback_Attempt_Status": "MATCH_SELECTED",
                "Fallback_Diagnostic": "Reference selected for descriptive review.",
            }
        ]
    ).to_csv(directory / "current_market_state_snapshot_fallback_trace.csv", index=False)
    pd.DataFrame([{"Snapshot_Evidence_Class": "CORE_SNAPSHOT_REFERENCE_EVIDENCE"}]).to_csv(
        directory / "current_market_state_snapshot_evidence_review.csv", index=False
    )
    pd.DataFrame([{"Snapshot_Query_Count": 1, "Snapshot_Result_Count": 1}]).to_csv(
        directory / "current_market_state_snapshot_behavior_summary.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "Diagnostic_Category": "SNAPSHOT_CONTEXT",
                "Diagnostic_Status": "VALID_SNAPSHOT_CONTEXT",
                "Diagnostic_Count": 1,
                "Diagnostic_Message": "Snapshot context loaded.",
            }
        ]
    ).to_csv(directory / "current_market_state_snapshot_diagnostic_review.csv", index=False)
    pd.DataFrame(
        [
            {
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT",
                "Snapshot_Source": "SAME_TIME_ALIGNMENT_LATEST_ROW",
                "Research_Reference_Count": 213,
                "Snapshot_Query_Count": 1,
                "Snapshot_Result_Count": 1,
                "Snapshot_Reference_Coverage_Ratio": 1.0,
                "Primary_Snapshot_Query_Match_Level": "D1_REGIME_CONTEXT_QUERY_MATCH",
                "Primary_Snapshot_Horizon": 1,
                "Current_Market_State_Snapshot_Readiness_Flag": "READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE",
            }
        ]
    ).to_csv(directory / "current_market_state_snapshot_research_summary.csv", index=False)
