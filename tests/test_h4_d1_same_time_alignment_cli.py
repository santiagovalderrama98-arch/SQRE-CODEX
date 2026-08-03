import subprocess
import sys
from pathlib import Path

from tests.h4_d1_same_time_alignment_test_utils import write_same_time_alignment_fixture


def test_cli_runs_with_synthetic_temp_data(tmp_path: Path):
    timestamped_dir, synchronized_dir = write_same_time_alignment_fixture(tmp_path)
    output_dir = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_d1_same_time_alignment_table.py",
            "--timestamped-state-regime-dir",
            str(timestamped_dir),
            "--synchronized-data-dir",
            str(synchronized_dir),
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
    assert "H4/D1 same-time alignment table generation completed" in result.stdout
    assert (output_dir / "h4_d1_same_time_alignment_summary.csv").exists()
