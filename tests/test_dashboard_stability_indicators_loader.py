from __future__ import annotations

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.loader import DashboardStabilityIndicatorsLoader


def write_synthetic_dashboard_stability_inputs(tmp_path) -> DashboardStabilityIndicatorsConfig:
    documentation_dir = tmp_path / "reference_stability_documentation"
    validation_dir = tmp_path / "reference_stability_validation"
    dashboard_dir = tmp_path / "research_dashboard_prototype"
    manual_dir = tmp_path / "manual_research_dashboard_review"
    output_dir = tmp_path / "dashboard_stability_indicators"
    for directory in [documentation_dir, validation_dir, dashboard_dir, manual_dir, output_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"Source_Name": ["validation"], "Load_Status": ["LOADED"]}).to_csv(
        documentation_dir / "reference_stability_documentation_source_inventory.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "Stability_Dimension": "Reference Population",
                "Observed_Stability_Class": "REFERENCE_POPULATION_STABLE",
                "Documentation_Class": "DOCUMENTED_STABLE_EVIDENCE",
                "Evidence_Usage_Policy_Class": "SAFE_FOR_MANUAL_RESEARCH_REVIEW",
            },
            {
                "Stability_Dimension": "Horizon Stability",
                "Observed_Stability_Class": "REFERENCE_HORIZON_PARTIAL",
                "Documentation_Class": "DOCUMENTED_PARTIAL_EVIDENCE",
                "Evidence_Usage_Policy_Class": "USE_WITH_STABILITY_WARNINGS",
            },
            {
                "Stability_Dimension": "Directional Consistency",
                "Observed_Stability_Class": "REFERENCE_DIRECTIONAL_UNSTABLE",
                "Documentation_Class": "DOCUMENTED_UNSTABLE_EVIDENCE",
                "Evidence_Usage_Policy_Class": "DOCUMENTATION_ONLY",
            },
        ]
    ).to_csv(documentation_dir / "reference_stability_interpretation_guide.csv", index=False)
    pd.DataFrame({"Evidence_Usage_Policy_Class": ["SAFE_FOR_MANUAL_RESEARCH_REVIEW"]}).to_csv(
        documentation_dir / "reference_evidence_usage_policy.csv", index=False
    )
    pd.DataFrame({"Dashboard_Guide_Element": ["Legend"], "Dashboard_Reading_Guide_Class": ["GUIDE_ELEMENT"]}).to_csv(
        documentation_dir / "reference_dashboard_reading_guide.csv", index=False
    )
    pd.DataFrame({"Limitation_Category": ["Snapshot"], "Limitation_Text": ["Research diagnostics only."]}).to_csv(
        documentation_dir / "reference_stability_limitations_documentation.csv", index=False
    )
    pd.DataFrame({"Follow_Up_Category": ["Usability"], "Follow_Up_Priority": ["MEDIUM"]}).to_csv(
        documentation_dir / "reference_stability_follow_up_plan.csv", index=False
    )
    pd.DataFrame(
        {
            "Reviewed_Source": ["documentation"],
            "Forbidden_Term": ["buy"],
            "Occurrence_Count": [0],
            "Documentation_Scope_Safety_Class": ["DOCUMENTATION_SCOPE_SAFE"],
        }
    ).to_csv(documentation_dir / "reference_stability_documentation_scope_safety_review.csv", index=False)
    pd.DataFrame(
        {
            "Symbol": ["EURUSD"],
            "Stability_Dimension_Count": [3],
            "Reference_Stability_Documentation_Readiness_Flag": ["PARTIAL_READY_FOR_DASHBOARD_STABILITY_INDICATORS"],
        }
    ).to_csv(documentation_dir / "reference_stability_documentation_summary.csv", index=False)
    (documentation_dir / "reference_stability_documentation_report.txt").write_text(
        "Reference stability documentation does not generate trading signals.\n", encoding="utf-8"
    )
    (documentation_dir / "reference_stability_documentation.md").write_text(
        "# Reference Stability Documentation\nThis documentation does not generate operational recommendations.\n",
        encoding="utf-8",
    )

    for filename in [
        "reference_population_review.csv",
        "reference_horizon_stability_review.csv",
        "reference_granularity_stability_review.csv",
        "reference_sample_adequacy_review.csv",
        "reference_dispersion_stability_review.csv",
        "reference_directional_consistency_review.csv",
        "reference_match_level_stability_review.csv",
        "dashboard_reference_stability_review.csv",
        "reference_stability_scorecard.csv",
        "reference_stability_validation_summary.csv",
    ]:
        pd.DataFrame({"Metric": ["rows"], "Value": [1]}).to_csv(validation_dir / filename, index=False)

    pd.DataFrame({"Snapshot_ID": ["SNAPSHOT_001"], "Snapshot_Query_Count": [3]}).to_csv(
        dashboard_dir / "research_dashboard_summary.csv", index=False
    )
    pd.DataFrame({"Snapshot_ID": ["SNAPSHOT_001"], "Snapshot_Context": ["Synthetic H4/D1 context"]}).to_csv(
        dashboard_dir / "research_dashboard_snapshot_panel.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "Reference_Card_ID": "CARD_001",
                "Snapshot_Query_ID": "Q1",
                "Requested_Forward_Horizon_H4_Candles": 12,
                "Matched_Research_Reference_ID": "REF_001",
                "Matched_Outcome_Profile_ID": "PROFILE_001",
                "Matched_Context_Granularity": "CONDITION",
                "Matched_Reference_Tier": "CORE",
                "Matched_Outcome_Sample_Size": 40,
                "Matched_Outcome_Dispersion_Pips": 8.5,
                "Matched_Directional_Behavior_Class": "DIRECTIONAL_BEHAVIOR_STABLE",
                "Matched_Horizon_Stability_Class": "HORIZON_STABLE",
                "Snapshot_Query_Match_Level": "EXACT_CONTEXT_MATCH",
                "Snapshot_Evidence_Class": "STABLE_EVIDENCE",
            },
            {
                "Reference_Card_ID": "CARD_002",
                "Snapshot_Query_ID": "Q2",
                "Requested_Forward_Horizon_H4_Candles": 12,
                "Matched_Research_Reference_ID": "REF_002",
                "Matched_Outcome_Profile_ID": "PROFILE_002",
                "Matched_Context_Granularity": "CONDITION",
                "Matched_Reference_Tier": "SUPPORTING",
                "Matched_Outcome_Sample_Size": 18,
                "Matched_Outcome_Dispersion_Pips": 14.2,
                "Matched_Directional_Behavior_Class": "DIRECTIONAL_BEHAVIOR_STABLE",
                "Matched_Horizon_Stability_Class": "HORIZON_PARTIAL",
                "Snapshot_Query_Match_Level": "BROADER_CONTEXT_FALLBACK",
                "Snapshot_Evidence_Class": "PARTIAL_EVIDENCE",
            },
            {
                "Reference_Card_ID": "CARD_003",
                "Snapshot_Query_ID": "Q3",
                "Requested_Forward_Horizon_H4_Candles": 12,
                "Matched_Research_Reference_ID": "REF_003",
                "Matched_Outcome_Profile_ID": "PROFILE_003",
                "Matched_Context_Granularity": "CONDITION",
                "Matched_Reference_Tier": "CORE",
                "Matched_Outcome_Sample_Size": 22,
                "Matched_Outcome_Dispersion_Pips": 16.0,
                "Matched_Directional_Behavior_Class": "DIRECTIONAL_BEHAVIOR_UNSTABLE",
                "Matched_Horizon_Stability_Class": "HORIZON_STABLE",
                "Snapshot_Query_Match_Level": "EXACT_CONTEXT_MATCH",
                "Snapshot_Evidence_Class": "WARNING_EVIDENCE",
            },
        ]
    ).to_csv(dashboard_dir / "research_dashboard_reference_cards.csv", index=False)
    pd.DataFrame({"Snapshot_Evidence_Class": ["STABLE_EVIDENCE"], "Snapshot_Result_Count": [3]}).to_csv(
        dashboard_dir / "research_dashboard_evidence_panel.csv", index=False
    )
    pd.DataFrame({"Snapshot_ID": ["SNAPSHOT_001"], "Snapshot_Result_Count": [3]}).to_csv(
        dashboard_dir / "research_dashboard_behavior_panel.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "Snapshot_Query_ID": "Q1",
                "Fallback_Attempt_Order": 1,
                "Attempted_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
                "Candidate_Reference_Count": 1,
                "Selected_Result_Count": 1,
                "Fallback_Attempt_Status": "MATCH_FOUND",
            },
            {
                "Snapshot_Query_ID": "Q2",
                "Fallback_Attempt_Order": 1,
                "Attempted_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
                "Candidate_Reference_Count": 0,
                "Selected_Result_Count": 0,
                "Fallback_Attempt_Status": "NO_MATCH_FOUND",
            },
            {
                "Snapshot_Query_ID": "Q2",
                "Fallback_Attempt_Order": 2,
                "Attempted_Match_Level": "D1_REGIME_CONTEXT_QUERY_MATCH",
                "Candidate_Reference_Count": 2,
                "Selected_Result_Count": 2,
                "Fallback_Attempt_Status": "MATCH_FOUND",
            },
            {
                "Snapshot_Query_ID": "Q3",
                "Fallback_Attempt_Order": 1,
                "Attempted_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
                "Candidate_Reference_Count": 0,
                "Selected_Result_Count": 0,
                "Fallback_Attempt_Status": "NO_MATCH_FOUND",
            },
            {
                "Snapshot_Query_ID": "Q3",
                "Fallback_Attempt_Order": 2,
                "Attempted_Match_Level": "D1_REGIME_CONTEXT_QUERY_MATCH",
                "Candidate_Reference_Count": 2,
                "Selected_Result_Count": 2,
                "Fallback_Attempt_Status": "MATCH_FOUND",
            },
            {
                "Snapshot_Query_ID": "Q4",
                "Fallback_Attempt_Order": 1,
                "Attempted_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
                "Candidate_Reference_Count": 0,
                "Selected_Result_Count": 0,
                "Fallback_Attempt_Status": "NO_MATCH_FOUND",
            },
        ]
    ).to_csv(dashboard_dir / "research_dashboard_fallback_panel.csv", index=False)
    pd.DataFrame({"Diagnostic": ["Synthetic dashboard diagnostic"]}).to_csv(
        dashboard_dir / "research_dashboard_diagnostic_panel.csv", index=False
    )
    (dashboard_dir / "research_dashboard_prototype_report.txt").write_text(
        "Dashboard prototype does not generate trading signals.\n", encoding="utf-8"
    )
    (dashboard_dir / "research_dashboard_prototype.html").write_text(
        "<html><body>Research dashboard does not generate operational recommendations.</body></html>\n",
        encoding="utf-8",
    )
    pd.DataFrame({"Manual_Review_Class": ["MANUAL_REVIEW_AVAILABLE"]}).to_csv(
        manual_dir / "manual_research_dashboard_review_summary.csv", index=False
    )
    pd.DataFrame({"Recommendation": ["Refine labels"]}).to_csv(
        manual_dir / "manual_research_dashboard_refinement_recommendations.csv", index=False
    )
    (manual_dir / "manual_research_dashboard_refined.html").write_text("<html><body>Manual review.</body></html>\n")

    return DashboardStabilityIndicatorsConfig(
        stability_documentation_dir=documentation_dir,
        stability_validation_dir=validation_dir,
        dashboard_dir=dashboard_dir,
        manual_dashboard_review_dir=manual_dir,
        output_dir=output_dir,
        report_path=output_dir / "dashboard_stability_indicators_report.txt",
        html_path=output_dir / "dashboard_stability_indicators.html",
    )


def test_loader_loads_required_and_optional_inputs(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    loader = DashboardStabilityIndicatorsLoader(config)
    frames = loader.load_frames()
    texts = loader.load_texts()

    assert len(frames["interpretation_guide"]) == 3
    assert len(frames["reference_cards"]) == 3
    assert "does not generate" in texts["documentation_report"]


def test_loader_handles_missing_required_inputs_safely(tmp_path):
    config = DashboardStabilityIndicatorsConfig(
        stability_documentation_dir=tmp_path / "missing_docs",
        stability_validation_dir=tmp_path / "missing_validation",
        dashboard_dir=tmp_path / "missing_dashboard",
        manual_dashboard_review_dir=tmp_path / "missing_manual",
        output_dir=tmp_path / "out",
    )

    loader = DashboardStabilityIndicatorsLoader(config)

    assert loader.load_frames()["interpretation_guide"].empty
    assert loader.load_texts()["documentation_report"] == ""
