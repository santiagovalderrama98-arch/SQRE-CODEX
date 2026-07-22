from pathlib import Path

import pandas as pd

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.h4_partial_complementary_dispersion_review_pipeline import (
    run_h4_partial_complementary_dispersion_review,
)


def test_pipeline_writes_all_expected_outputs_and_report(tmp_path: Path):
    partial_dir = _write_partial_inputs(tmp_path)
    transition_sensitive_dir = tmp_path / "transition_sensitive"
    transition_sensitive_dir.mkdir()
    pd.DataFrame(
        [{"H4_Transition_Scenario_Sensitive_Profile": "HIGH_TRANSITION_SCENARIO_SENSITIVITY", "High_Sensitivity_Profile_Count": 9}]
    ).to_csv(transition_sensitive_dir / "h4_transition_scenario_sensitive_review_summary.csv", index=False)
    output_dir = tmp_path / "out"
    report = output_dir / "h4_partial_complementary_dispersion_review_report.txt"

    result = run_h4_partial_complementary_dispersion_review(
        H4PartialComplementaryDispersionReviewConfig(
            partial_validation_dir=partial_dir,
            h4_transition_sensitive_dir=transition_sensitive_dir,
            output_dir=output_dir,
            report_path=report,
        )
    )

    expected = [
        "h4_partial_complement_source_inventory.csv",
        "h4_partial_sample_review_inventory.csv",
        "h4_partial_state_complement_review.csv",
        "h4_partial_transition_complement_review.csv",
        "h4_partial_sensitivity_complement_review.csv",
        "h4_partial_baseline_interpretation_matrix.csv",
        "h4_partial_sample_caveat_review.csv",
        "h4_partial_complementary_dispersion_summary.csv",
    ]
    assert all((output_dir / name).exists() for name in expected)
    assert report.exists()
    assert result.summary is not None


def _write_partial_inputs(tmp_path: Path) -> Path:
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "Coverage_Ratio": 0.5}]).to_csv(partial_dir / "h4_partial_candidate_inventory.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "Run_Status": "COMPLETED", "Condition_Profile_Count": 48}]).to_csv(partial_dir / "h4_partial_validation_run_summary.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "Sample_Adequacy_Class": "PARTIAL_SAMPLE_RESEARCH_USABLE"}]).to_csv(partial_dir / "h4_partial_sample_adequacy_review.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "Partial_Comparison_Class": "CONSISTENT_WITH_BASELINE_RANGE"}]).to_csv(partial_dir / "h4_partial_vs_baseline_comparison.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "State_Diversity_Profile": "DIVERSE_STATE_SAMPLE", "Unique_State_Count": 4, "Most_Common_State": "DIRECTIONAL"}]).to_csv(partial_dir / "h4_partial_structure_state_summary.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "Most_Common_Transition": "A_TO_B", "Unique_Transition_Count": 5}]).to_csv(partial_dir / "h4_partial_transition_summary.csv", index=False)
    return partial_dir
