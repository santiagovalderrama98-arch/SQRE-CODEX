import subprocess
import sys
from pathlib import Path

from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_cli_runs_with_synthetic_synchronized_inputs(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync")
    output_dir = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_timestamped_h4_d1_state_regime_generation.py",
            "--synchronized-data-dir",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(output_dir / "report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Timestamped H4/D1 state and regime generation completed" in result.stdout
    assert (output_dir / "timestamped_h4_d1_state_regime_summary.csv").exists()
