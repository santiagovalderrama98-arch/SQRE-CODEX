import subprocess
import sys
from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs


def test_cli_runs_with_synthetic_inputs(tmp_path: Path):
    dispersion_dir, deep_dive_dir = write_transition_sensitive_inputs(tmp_path)
    output_dir = tmp_path / "out"
    report = output_dir / "report.txt"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_transition_scenario_sensitive_review.py",
            "--dispersion-review-dir",
            str(dispersion_dir),
            "--transition-deep-dive-dir",
            str(deep_dive_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "H4 transition scenario-sensitive review completed" in result.stdout
    assert report.exists()
