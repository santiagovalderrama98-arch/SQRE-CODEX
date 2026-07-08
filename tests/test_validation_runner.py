from types import SimpleNamespace

import pandas as pd

from sqre.validation.models import COMPLETED, FAILED, MISSING_INPUT
from sqre.validation.runner import run_multi_scenario_validation


def test_validation_runner_marks_missing_input(tmp_path):
    config_path = _config(tmp_path, "missing.csv")

    summary, results, metrics = run_multi_scenario_validation(
        config_path=config_path,
        output_dir=tmp_path / "validation",
        report_path=tmp_path / "validation" / "report.txt",
        summary_csv_path=tmp_path / "validation" / "summary.csv",
    )

    assert summary.scenarios_missing_input == 1
    assert results[0].status == MISSING_INPUT
    assert metrics[0].status == MISSING_INPUT
    assert (tmp_path / "validation" / "summary.csv").exists()
    assert (tmp_path / "validation" / "report.txt").exists()


def test_validation_runner_executes_all_steps_with_mocked_commands(tmp_path):
    ohlc_path = tmp_path / "EURUSD_M5.csv"
    pd.DataFrame(
        [{"Date": "2026-01-01 00:00:00", "Open": 1.1, "High": 1.2, "Low": 1.0, "Close": 1.15, "Volume": 0}]
    ).to_csv(ohlc_path, index=False)
    config_path = _config(tmp_path, str(ohlc_path))
    calls = []

    def command_runner(command, cwd):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    summary, results, _metrics = run_multi_scenario_validation(
        config_path=config_path,
        output_dir=tmp_path / "validation",
        report_path=tmp_path / "validation" / "report.txt",
        summary_csv_path=tmp_path / "validation" / "summary.csv",
        command_runner=command_runner,
    )

    assert summary.scenarios_completed == 1
    assert results[0].status == COMPLETED
    assert len(calls) == 6
    assert any("run_price_outcome_research.py" in part for command in calls for part in command)


def test_validation_runner_records_command_failure(tmp_path):
    ohlc_path = tmp_path / "EURUSD_M5.csv"
    pd.DataFrame(
        [{"Date": "2026-01-01 00:00:00", "Open": 1.1, "High": 1.2, "Low": 1.0, "Close": 1.15, "Volume": 0}]
    ).to_csv(ohlc_path, index=False)
    config_path = _config(tmp_path, str(ohlc_path))

    def command_runner(command, cwd):
        return SimpleNamespace(returncode=2, stdout="", stderr="example failure")

    summary, results, _metrics = run_multi_scenario_validation(
        config_path=config_path,
        output_dir=tmp_path / "validation",
        report_path=tmp_path / "validation" / "report.txt",
        summary_csv_path=tmp_path / "validation" / "summary.csv",
        command_runner=command_runner,
    )

    assert summary.scenarios_failed == 1
    assert results[0].status == FAILED
    assert "example failure" in results[0].message


def _config(tmp_path, ohlc_path: str):
    config_path = tmp_path / "validation.yaml"
    config_path.write_text(
        f"""
validation_name: sample_validation
symbol: EURUSD
pip_size: 0.0001
minimum_sample_size: 5

scenarios:
  - scenario_id: eurusd_m5
    symbol: EURUSD
    timeframe: M5
    ohlc_path: {ohlc_path}
    max_structure_duration_seconds: 14400
    forward_candles: [3, 6, 12]
""",
        encoding="utf-8",
    )
    return config_path
