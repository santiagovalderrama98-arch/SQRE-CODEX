import subprocess
import sys
from pathlib import Path

from test_h4_expanded_sample_feasibility_pipeline import write_pipeline_inputs


def test_cli_runs_with_synthetic_inputs(tmp_path: Path):
    config = write_pipeline_inputs(tmp_path)
    output_dir = tmp_path / "out"
    report = output_dir / "report.txt"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_expanded_sample_feasibility_review.py",
            "--sample-config",
            str(config.sample_config),
            "--expanded-validation-config",
            str(config.expanded_validation_config),
            "--h4-d1-validation-config",
            str(config.h4_d1_validation_config),
            "--availability-csv",
            str(config.availability_csv),
            "--master-summary-csv",
            str(config.master_summary_csv),
            "--expanded-summary-csv",
            str(config.expanded_summary_csv),
            "--h4-d1-validation-summary",
            str(config.h4_d1_validation_summary),
            "--h4-d1-research-dir",
            str(config.h4_d1_research_dir),
            "--raw-data-dir",
            str(config.raw_data_dir),
            "--partial-data-dir",
            str(config.partial_data_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "H4 expanded sample feasibility review completed" in completed.stdout
    assert "Feasibility matrix rows: 2" in completed.stdout
    assert report.exists()
