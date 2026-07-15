from pathlib import Path

import pandas as pd

from sqre.d1_state_outcome_deep_dive.d1_state_outcome_deep_dive_pipeline import run_d1_state_outcome_deep_dive


EXPECTED_OUTPUTS = [
    "d1_state_deep_dive_profile_inventory.csv",
    "d1_state_regime_breakdown.csv",
    "d1_state_outcome_statistics.csv",
    "d1_state_regime_comparison_matrix.csv",
    "d1_state_deep_dive_summary.csv",
]


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    outcome_review_dir = tmp_path / "review"
    regime_research_dir = tmp_path / "regime"
    output_dir = tmp_path / "output"
    report_path = output_dir / "d1_state_outcome_deep_dive_report.txt"
    _write_inputs(outcome_review_dir, regime_research_dir)

    result = run_d1_state_outcome_deep_dive(outcome_review_dir, regime_research_dir, output_dir, report_path)

    assert len(result.selected_profiles) == 2
    assert len(result.regime_breakdown_rows) == 4
    assert len(result.outcome_statistics_rows) == 2
    assert len(result.comparison_rows) == 4
    assert len(result.summary_rows) == 2
    for filename in EXPECTED_OUTPUTS:
        assert (output_dir / filename).exists()
    assert report_path.exists()

    summary = pd.read_csv(output_dir / "d1_state_deep_dive_summary.csv")
    assert set(summary["Condition_Label"]) == {"DIRECTIONAL_DISPLACEMENT", "DIRECTIONAL_EXPANSION"}


def _write_inputs(outcome_review_dir: Path, regime_research_dir: Path) -> None:
    outcome_review_dir.mkdir()
    regime_research_dir.mkdir()
    (outcome_review_dir / "d1_research_ready_condition_profiles.csv").write_text(
        "\n".join(
            [
                "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Total_Sample_Size,"
                "Average_Forward_Range_Pips,Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,"
                "Forward_Range_CV,Outcome_Magnitude_CV,Condition_Research_Class",
                "STATE_CONDITION,DIRECTIONAL_EXPANSION,3,2,70,15,6,0.6,0.1,0.1,RESEARCH_READY_DESCRIPTIVE",
            ]
        ),
        encoding="utf-8",
    )
    (outcome_review_dir / "d1_regime_sensitive_condition_profiles.csv").write_text(
        "\n".join(
            [
                "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Total_Sample_Size,"
                "Average_Forward_Range_Pips,Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,"
                "Forward_Range_CV,Outcome_Magnitude_CV,Condition_Research_Class",
                "STATE_CONDITION,DIRECTIONAL_DISPLACEMENT,3,2,70,15,6,0.6,0.4,0.1,REGIME_SENSITIVE_REVIEW",
                "STATE_CONDITION,DIRECTIONAL_EXPANSION,6,2,70,15,6,0.6,0.4,0.1,REGIME_SENSITIVE_REVIEW",
            ]
        ),
        encoding="utf-8",
    )
    (regime_research_dir / "d1_regime_condition_outcomes.csv").write_text(
        "\n".join(
            [
                "Regime_ID,Regime_Label,Scenario_ID,Timeframe,Condition_Type,Condition_Label,Forward_Window,"
                "Sample_Size,Average_Forward_Close_Return_Pips,Median_Forward_Close_Return_Pips,"
                "Average_Forward_Range_Pips,Average_Favorable_Displacement_Pips,Average_Adverse_Displacement_Pips,"
                "Average_Outcome_Magnitude_Pips,Direction_Alignment_Rate,Sample_Adequacy_Flag",
                "R1,Regime 1,S1,D1,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,30,1,1,10,8,2,4,0.5,ADEQUATE",
                "R2,Regime 2,S2,D1,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,40,3,3,20,14,3,8,0.7,ADEQUATE",
                "R1,Regime 1,S1,D1,STATE_CONDITION,DIRECTIONAL_DISPLACEMENT,3,30,2,2,12,9,2,5,0.4,ADEQUATE",
                "R2,Regime 2,S2,D1,STATE_CONDITION,DIRECTIONAL_DISPLACEMENT,3,40,4,4,18,13,3,7,0.8,ADEQUATE",
            ]
        ),
        encoding="utf-8",
    )
