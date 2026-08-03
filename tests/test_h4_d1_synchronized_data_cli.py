import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_cli_runs_with_synthetic_h4_input(tmp_path: Path):
    h4_input = tmp_path / "EURUSD_H4.csv"
    output_dir = tmp_path / "out"
    pd.DataFrame(
        {
            "Date": [
                "2026-07-01 00:00:00",
                "2026-07-01 04:00:00",
                "2026-07-01 08:00:00",
                "2026-07-01 12:00:00",
                "2026-07-01 16:00:00",
                "2026-07-01 20:00:00",
            ],
            "Open": [1, 2, 3, 4, 5, 6],
            "High": [2, 3, 4, 5, 6, 7],
            "Low": [0, 1, 2, 3, 4, 5],
            "Close": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
            "Volume": [1, 1, 1, 1, 1, 1],
        }
    ).to_csv(h4_input, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_d1_synchronized_data_preparation.py",
            "--symbol",
            "EURUSD",
            "--h4-input",
            str(h4_input),
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
    assert "H4/D1 synchronized data preparation completed" in result.stdout
    assert (output_dir / "report.txt").exists()
