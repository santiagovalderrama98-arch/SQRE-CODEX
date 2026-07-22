import subprocess
import sys
from pathlib import Path


def test_cli_runs_with_missing_inputs(tmp_path: Path):
    script = Path("scripts/run_h4_transition_state_combined_context_review.py")
    output_dir = tmp_path / "out"
    report = output_dir / "report.txt"

    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report),
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0
    assert "H4 transition/state combined context review completed" in completed.stdout
    assert report.exists()
