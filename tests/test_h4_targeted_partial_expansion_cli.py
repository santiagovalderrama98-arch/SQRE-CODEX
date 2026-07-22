import subprocess
import sys
from pathlib import Path

from test_h4_targeted_partial_expansion_helpers import write_baseline_inputs, write_feasibility_inputs


def test_cli_runs_with_synthetic_missing_raw(tmp_path: Path):
    feasibility_dir = write_feasibility_inputs(tmp_path)
    baseline_validation_dir, baseline_research_dir = write_baseline_inputs(tmp_path)
    output_dir = tmp_path / "validation"
    research_dir = tmp_path / "research"
    report = research_dir / "report.txt"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_targeted_partial_expansion_validation.py",
            "--feasibility-dir",
            str(feasibility_dir),
            "--baseline-validation-dir",
            str(baseline_validation_dir),
            "--baseline-research-dir",
            str(baseline_research_dir),
            "--output-dir",
            str(output_dir),
            "--research-output-dir",
            str(research_dir),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "H4 targeted partial expansion validation completed" in result.stdout
    assert report.exists()
