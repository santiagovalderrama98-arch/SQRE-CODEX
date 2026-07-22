from pathlib import Path
import subprocess
import sys

import pandas as pd


def test_cli_works_with_synthetic_data(tmp_path: Path):
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "Coverage_Ratio": 0.5}]).to_csv(partial_dir / "h4_partial_candidate_inventory.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Label": "PARTIAL_SAMPLE", "Run_Status": "COMPLETED", "Condition_Profile_Count": 48}]).to_csv(partial_dir / "h4_partial_validation_run_summary.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Adequacy_Class": "PARTIAL_SAMPLE_RESEARCH_USABLE"}]).to_csv(partial_dir / "h4_partial_sample_adequacy_review.csv", index=False)
    pd.DataFrame([{"Candidate_ID": "eurusd_h4_period_5_partial", "Partial_Comparison_Class": "CONSISTENT_WITH_BASELINE_RANGE"}]).to_csv(partial_dir / "h4_partial_vs_baseline_comparison.csv", index=False)
    output_dir = tmp_path / "out"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_partial_complementary_dispersion_review.py",
            "--partial-validation-dir",
            str(partial_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(output_dir / "report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "H4 partial complementary dispersion review completed" in completed.stdout
    assert (output_dir / "h4_partial_complementary_dispersion_summary.csv").exists()
