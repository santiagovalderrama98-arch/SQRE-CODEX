from pathlib import Path

import pandas as pd

from sqre.d1_regime_outcome_review.d1_regime_outcome_review_pipeline import run_d1_regime_outcome_review


EXPECTED_OUTPUTS = [
    "d1_condition_quality_inventory.csv",
    "d1_research_ready_condition_profiles.csv",
    "d1_regime_sensitive_condition_profiles.csv",
    "d1_low_sample_condition_profiles.csv",
    "d1_limited_coverage_condition_profiles.csv",
    "d1_state_condition_quality_summary.csv",
    "d1_transition_condition_quality_summary.csv",
    "d1_outcome_dispersion_summary.csv",
    "d1_sample_adequacy_summary.csv",
    "d1_regime_outcome_review_summary.csv",
]


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    report_path = output_dir / "d1_regime_outcome_review_report.txt"
    _write_profiles(input_dir)

    result = run_d1_regime_outcome_review(input_dir, output_dir, report_path)

    assert result.profiles_loaded == 4
    for filename in EXPECTED_OUTPUTS:
        assert (output_dir / filename).exists()
    assert report_path.exists()

    summary = pd.read_csv(output_dir / "d1_regime_outcome_review_summary.csv")
    assert summary.loc[0, "Timeframe"] == "D1"
    assert summary.loc[0, "Input_Profile_Count"] == 4
    assert summary.loc[0, "Low_Sample_Profile_Count"] == 1


def _write_profiles(input_dir: Path) -> None:
    input_dir.mkdir()
    (input_dir / "d1_regime_normalized_condition_profiles.csv").write_text(
        "\n".join(
            [
                "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Total_Sample_Size,"
                "Average_Forward_Range_Pips,Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,"
                "Forward_Range_CV,Outcome_Magnitude_CV,Regime_Sensitivity_Flag",
                "STATE,EXPANSION,20,4,80,22.5,8.0,0.61,0.12,0.18,STABLE",
                "STATE,COMPRESSION,20,4,8,12.5,3.0,0.51,0.14,0.18,STABLE",
                "TRANSITION,A_TO_B,20,4,90,24.5,9.0,0.57,0.42,0.18,HIGH",
                "TRANSITION,B_TO_C,20,1,70,10.5,2.0,0.49,0.10,0.10,STABLE",
            ]
        ),
        encoding="utf-8",
    )
