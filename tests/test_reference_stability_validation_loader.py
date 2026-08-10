from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.loader import ReferenceStabilityValidationLoader


def reference_store_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Research_Reference_ID": "RRS_1",
                "Context_Granularity": "H4_TRANSITION_ONLY",
                "Forward_Horizon_H4_Candles": 1,
                "Outcome_Sample_Size": 30,
                "Outcome_Dispersion_Pips": 35,
                "Reference_Tier": "CORE_RESEARCH_REFERENCE",
                "Directional_Behavior_Class": "DIRECTIONAL_BEHAVIOR_CONSISTENT",
                "Dominant_Observed_Direction": "UP",
            },
            {
                "Research_Reference_ID": "RRS_2",
                "Context_Granularity": "H4_D1_REGIME",
                "Forward_Horizon_H4_Candles": 2,
                "Outcome_Sample_Size": 12,
                "Outcome_Dispersion_Pips": 70,
                "Reference_Tier": "SUPPORTING_RESEARCH_REFERENCE",
                "Directional_Behavior_Class": "MIXED_DIRECTIONAL_BEHAVIOR",
                "Dominant_Observed_Direction": "DOWN",
            },
            {
                "Research_Reference_ID": "RRS_3",
                "Context_Granularity": "H4_D1_REGIME",
                "Forward_Horizon_H4_Candles": 2,
                "Outcome_Sample_Size": 5,
                "Outcome_Dispersion_Pips": 95,
                "Reference_Tier": "CORE_RESEARCH_REFERENCE",
                "Directional_Behavior_Class": "DIRECTIONAL_BEHAVIOR_UNSTABLE",
                "Dominant_Observed_Direction": "UP",
            },
        ]
    )


def query_results_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Research_Query_Result_ID": "RQR_1",
                "Research_Query_ID": "RQ_1",
                "Research_Query_Match_Level": "D1_REGIME_CONTEXT_QUERY_MATCH",
                "Matched_Reference_Tier": "CORE_REFERENCE",
                "Matched_Outcome_Sample_Size": 30,
                "Matched_Outcome_Dispersion_Pips": 35,
            },
            {
                "Research_Query_Result_ID": "RQR_2",
                "Research_Query_ID": "RQ_2",
                "Research_Query_Match_Level": "BROADER_H4_TRANSITION_ANY_HORIZON_QUERY_MATCH",
                "Matched_Reference_Tier": "SUPPORTING_REFERENCE",
                "Matched_Outcome_Sample_Size": 8,
                "Matched_Outcome_Dispersion_Pips": 90,
            },
        ]
    )


def dashboard_cards_frame() -> pd.DataFrame:
    rows = []
    for index in range(5):
        rows.append(
            {
                "Reference_Card_ID": f"CARD_{index}",
                "Matched_Reference_Tier": "CORE_REFERENCE",
                "Matched_Forward_Horizon_H4_Candles": 1,
                "Snapshot_Query_Match_Level": "D1_REGIME_CONTEXT_QUERY_MATCH",
                "Matched_Outcome_Sample_Size": 30,
                "Matched_Outcome_Dispersion_Pips": 35,
            }
        )
    return pd.DataFrame(rows)


def write_synthetic_inputs(root: Path) -> ReferenceStabilityValidationConfig:
    reference_dir = root / "reference"
    query_dir = root / "query"
    snapshot_dir = root / "snapshot"
    dashboard_dir = root / "dashboard"
    manual_dir = root / "manual"
    for directory in [reference_dir, query_dir, snapshot_dir, dashboard_dir, manual_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    reference_store_frame().to_csv(reference_dir / "research_reference_store.csv", index=False)
    reference_store_frame().to_csv(reference_dir / "research_reference_candidates.csv", index=False)
    pd.DataFrame({"Review": ["ok"]}).to_csv(reference_dir / "research_reference_exclusion_review.csv", index=False)
    pd.DataFrame({"Context_Granularity": ["H4_TRANSITION_ONLY"]}).to_csv(reference_dir / "research_reference_granularity_review.csv", index=False)
    pd.DataFrame({"Forward_Horizon_H4_Candles": [1]}).to_csv(reference_dir / "research_reference_horizon_review.csv", index=False)
    pd.DataFrame({"Included_Reference_Count": [3]}).to_csv(reference_dir / "research_reference_store_design_summary.csv", index=False)
    pd.DataFrame({"Research_Query_ID": ["RQ_1", "RQ_2"]}).to_csv(query_dir / "research_query_requests.csv", index=False)
    query_results_frame().to_csv(query_dir / "research_query_results.csv", index=False)
    pd.DataFrame({"Trace": ["ok"]}).to_csv(query_dir / "research_query_fallback_trace.csv", index=False)
    pd.DataFrame({"Review": ["ok"]}).to_csv(query_dir / "research_query_evidence_quality_review.csv", index=False)
    pd.DataFrame({"Research_Query_Coverage_Ratio": [1.0]}).to_csv(query_dir / "research_query_coverage_review.csv", index=False)
    pd.DataFrame({"Review": ["ok"]}).to_csv(query_dir / "research_query_result_quality_review.csv", index=False)
    pd.DataFrame({"Query_Result_Count": [2]}).to_csv(query_dir / "research_query_interface_design_summary.csv", index=False)
    pd.DataFrame({"Snapshot": ["ok"]}).to_csv(snapshot_dir / "current_market_state_snapshot_context.csv", index=False)
    pd.DataFrame({"Snapshot": ["ok"]}).to_csv(snapshot_dir / "current_market_state_snapshot_reference_results.csv", index=False)
    pd.DataFrame({"Snapshot": ["ok"]}).to_csv(snapshot_dir / "current_market_state_snapshot_behavior_summary.csv", index=False)
    pd.DataFrame({"Snapshot": ["ok"]}).to_csv(snapshot_dir / "current_market_state_snapshot_research_summary.csv", index=False)
    dashboard_cards_frame().to_csv(dashboard_dir / "research_dashboard_reference_cards.csv", index=False)
    pd.DataFrame({"Reference_Card_Count": [5]}).to_csv(dashboard_dir / "research_dashboard_summary.csv", index=False)
    pd.DataFrame({"Panel": ["ok"]}).to_csv(dashboard_dir / "research_dashboard_behavior_panel.csv", index=False)
    pd.DataFrame({"Panel": ["ok"]}).to_csv(dashboard_dir / "research_dashboard_evidence_panel.csv", index=False)
    pd.DataFrame({"Scope_Safety_Class": ["SCOPE_SAFE"]}).to_csv(
        manual_dir / "manual_research_dashboard_review_summary.csv", index=False
    )
    pd.DataFrame({"Recommendation_ID": ["R1"]}).to_csv(
        manual_dir / "manual_research_dashboard_refinement_recommendations.csv", index=False
    )
    return ReferenceStabilityValidationConfig(
        reference_store_dir=reference_dir,
        query_interface_dir=query_dir,
        snapshot_research_dir=snapshot_dir,
        dashboard_dir=dashboard_dir,
        manual_dashboard_review_dir=manual_dir,
        output_dir=root / "out",
        report_path=root / "out" / "reference_stability_validation_report.txt",
    )


def test_loader_loads_reference_store_and_query_interface_outputs(tmp_path):
    config = write_synthetic_inputs(tmp_path)
    frames = ReferenceStabilityValidationLoader(config).load_frames()

    assert len(frames["reference_store"]) == 3
    assert len(frames["query_results"]) == 2
    assert len(frames["dashboard_reference_cards"]) == 5


def test_loader_handles_missing_required_inputs_safely(tmp_path):
    config = ReferenceStabilityValidationConfig(
        reference_store_dir=tmp_path / "missing_reference",
        query_interface_dir=tmp_path / "missing_query",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )

    frames = ReferenceStabilityValidationLoader(config).load_frames()

    assert frames["reference_store"].empty
    assert frames["query_results"].empty
