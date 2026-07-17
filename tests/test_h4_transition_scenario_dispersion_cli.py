from pathlib import Path
import subprocess
import sys

from test_h4_transition_scenario_dispersion_review_loader import write_review_inputs


def test_cli_runs_with_synthetic_data(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    report_path = output_dir / "report.txt"
    write_review_inputs(input_dir)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_transition_scenario_dispersion_review.py",
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "H4 transition scenario dispersion review completed" in result.stdout
    assert "Profile dispersion diagnostics: 4" in result.stdout
    assert (output_dir / "h4_transition_scenario_dispersion_review_summary.csv").exists()
