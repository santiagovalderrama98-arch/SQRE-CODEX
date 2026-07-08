import subprocess
import sys


def test_multi_scenario_validation_cli_handles_missing_input(tmp_path):
    config_path = tmp_path / "validation.yaml"
    output_dir = tmp_path / "validation"
    report_path = output_dir / "report.txt"
    summary_path = output_dir / "summary.csv"
    config_path.write_text(
        """
validation_name: cli_validation
symbol: EURUSD
pip_size: 0.0001
minimum_sample_size: 5

scenarios:
  - scenario_id: missing_case
    symbol: EURUSD
    timeframe: M5
    ohlc_path: missing.csv
    max_structure_duration_seconds: 14400
    forward_candles: [3, 6, 12]
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_multi_scenario_validation.py",
            "--config",
            str(config_path),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
            "--summary-csv",
            str(summary_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "SQRE multi-scenario validation started" in completed.stdout
    assert "Status: MISSING_INPUT" in completed.stdout
    assert report_path.exists()
    assert summary_path.exists()
