from pathlib import Path
import subprocess
import sys

from h4_state_deep_dive_test_utils import write_h4_deep_dive_inputs


def test_cli_runs_with_synthetic_data(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    output_dir = tmp_path / "output"
    report_path = output_dir / "report.txt"
    write_h4_deep_dive_inputs(research_dir, validation_dir)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_state_outcome_deep_dive.py",
            "--h4-d1-research-dir",
            str(research_dir),
            "--validation-output-dir",
            str(validation_dir),
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
    assert "H4 state outcome deep dive completed" in result.stdout
    assert "Selected profiles: 3" in result.stdout
    assert (output_dir / "h4_state_deep_dive_summary.csv").exists()
    assert report_path.exists()
