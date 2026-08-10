from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig
from sqre.reference_stability_documentation.loader import ReferenceStabilityDocumentationLoader


def write_synthetic_documentation_inputs(root: Path) -> ReferenceStabilityDocumentationConfig:
    stability_dir = root / "stability"
    dashboard_dir = root / "dashboard"
    manual_dir = root / "manual"
    output_dir = root / "out"
    for directory in [stability_dir, dashboard_dir, manual_dir, output_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"Source_Name": ["reference_store"], "Load_Status": ["LOADED"]}).to_csv(
        stability_dir / "reference_stability_source_inventory.csv", index=False
    )
    pd.DataFrame({"Reference_Count": [213], "Core_Reference_Count": [51], "Supporting_Reference_Count": [162]}).to_csv(
        stability_dir / "reference_population_review.csv", index=False
    )
    pd.DataFrame({"Horizon_Stability_Class": ["PARTIAL_HORIZON_STABILITY"]}).to_csv(
        stability_dir / "reference_horizon_stability_review.csv", index=False
    )
    pd.DataFrame({"Granularity_Stability_Class": ["PARTIAL_GRANULARITY_CONTEXT"]}).to_csv(
        stability_dir / "reference_granularity_stability_review.csv", index=False
    )
    pd.DataFrame({"Sample_Adequacy_Class": ["STABLE_SAMPLE_SIZE"]}).to_csv(
        stability_dir / "reference_sample_adequacy_review.csv", index=False
    )
    pd.DataFrame({"Dispersion_Stability_Class": ["STABLE_DISPERSION"]}).to_csv(
        stability_dir / "reference_dispersion_stability_review.csv", index=False
    )
    pd.DataFrame({"Directional_Consistency_Class": ["DIRECTIONAL_BEHAVIOR_UNSTABLE"]}).to_csv(
        stability_dir / "reference_directional_consistency_review.csv", index=False
    )
    pd.DataFrame({"Match_Level_Stability_Class": ["FALLBACK_DEPENDENT_MATCH_USAGE"]}).to_csv(
        stability_dir / "reference_match_level_stability_review.csv", index=False
    )
    pd.DataFrame({"Dashboard_Reference_Stability_Class": ["DASHBOARD_REFERENCES_PARTIAL_FOR_REVIEW"]}).to_csv(
        stability_dir / "dashboard_reference_stability_review.csv", index=False
    )
    pd.DataFrame(
        [
            {"Stability_Dimension": "Reference Population", "Dominant_Stability_Class": "REFERENCE_POPULATION_AVAILABLE"},
            {"Stability_Dimension": "Horizon Stability", "Dominant_Stability_Class": "PARTIAL_HORIZON_STABILITY"},
            {"Stability_Dimension": "Granularity Stability", "Dominant_Stability_Class": "PARTIAL_GRANULARITY_CONTEXT"},
            {"Stability_Dimension": "Sample Adequacy", "Dominant_Stability_Class": "STABLE_SAMPLE_SIZE"},
            {"Stability_Dimension": "Dispersion Stability", "Dominant_Stability_Class": "STABLE_DISPERSION"},
            {"Stability_Dimension": "Directional Consistency", "Dominant_Stability_Class": "DIRECTIONAL_BEHAVIOR_UNSTABLE"},
            {"Stability_Dimension": "Match Level Stability", "Dominant_Stability_Class": "FALLBACK_DEPENDENT_MATCH_USAGE"},
            {"Stability_Dimension": "Dashboard Reference Stability", "Dominant_Stability_Class": "DASHBOARD_REFERENCES_PARTIAL_FOR_REVIEW"},
        ]
    ).to_csv(stability_dir / "reference_stability_scorecard.csv", index=False)
    pd.DataFrame(
        {
            "Reference_Count": [213],
            "Core_Reference_Count": [51],
            "Supporting_Reference_Count": [162],
            "Partial_Horizon_Count": [5],
            "Partial_Granularity_Count": [3],
            "Stable_Sample_Group_Count": [24],
            "Stable_Dispersion_Group_Count": [40],
            "Fallback_Dependent_Match_Level_Count": [2],
            "Dashboard_Reference_Card_Count": [10],
        }
    ).to_csv(stability_dir / "reference_stability_validation_summary.csv", index=False)
    (stability_dir / "reference_stability_validation_report.txt").write_text(
        "This phase does not generate trading signals.\n", encoding="utf-8"
    )

    pd.DataFrame({"Reference_Card_ID": ["CARD_1"]}).to_csv(
        dashboard_dir / "research_dashboard_reference_cards.csv", index=False
    )
    pd.DataFrame({"Reference_Card_Count": [10]}).to_csv(dashboard_dir / "research_dashboard_summary.csv", index=False)
    (dashboard_dir / "research_dashboard_prototype_report.txt").write_text("Dashboard report\n", encoding="utf-8")
    (dashboard_dir / "research_dashboard_prototype.html").write_text("<html></html>\n", encoding="utf-8")

    pd.DataFrame({"Scope_Safety_Class": ["SCOPE_SAFE"]}).to_csv(
        manual_dir / "manual_research_dashboard_review_summary.csv", index=False
    )
    pd.DataFrame({"Recommendation_ID": ["REC_1"]}).to_csv(
        manual_dir / "manual_research_dashboard_refinement_recommendations.csv", index=False
    )
    (manual_dir / "manual_research_dashboard_review_report.txt").write_text("Manual review\n", encoding="utf-8")
    (manual_dir / "manual_research_dashboard_refined.html").write_text("<html></html>\n", encoding="utf-8")

    return ReferenceStabilityDocumentationConfig(
        stability_validation_dir=stability_dir,
        dashboard_dir=dashboard_dir,
        manual_dashboard_review_dir=manual_dir,
        output_dir=output_dir,
        report_path=output_dir / "reference_stability_documentation_report.txt",
        markdown_path=output_dir / "reference_stability_documentation.md",
    )


def test_loader_loads_stability_validation_outputs(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)

    frames = ReferenceStabilityDocumentationLoader(config).load_frames()
    texts = ReferenceStabilityDocumentationLoader(config).load_texts()

    assert len(frames["reference_stability_scorecard"]) == 8
    assert len(frames["research_dashboard_reference_cards"]) == 1
    assert "does not generate trading signals" in texts["reference_stability_validation_report"]


def test_loader_handles_missing_required_inputs_safely(tmp_path):
    config = ReferenceStabilityDocumentationConfig(
        stability_validation_dir=tmp_path / "missing",
        dashboard_dir=tmp_path / "dashboard",
        manual_dashboard_review_dir=tmp_path / "manual",
        output_dir=tmp_path / "out",
    )

    frames = ReferenceStabilityDocumentationLoader(config).load_frames()

    assert frames["reference_stability_scorecard"].empty
    assert frames["reference_stability_validation_summary"].empty
