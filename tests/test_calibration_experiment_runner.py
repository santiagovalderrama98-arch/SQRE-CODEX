from pathlib import Path
from subprocess import CompletedProcess

import pytest

from sqre.calibration_experiments.models import ExperimentRun
from sqre.calibration_experiments.runner import CalibrationExperimentRunner


def _run(tmp_path: Path, ohlc_path: Path) -> ExperimentRun:
    output_dir = tmp_path / "out" / "duration_baseline" / "eurusd_h4_period_1"
    return ExperimentRun(
        experiment_run_id="duration_baseline__eurusd_h4_period_1",
        experiment_type="DURATION",
        experiment_id="duration_baseline",
        scenario_id="eurusd_h4_period_1",
        symbol="EURUSD",
        timeframe="H4",
        ohlc_path=ohlc_path,
        max_structure_duration_seconds=604800,
        minimum_sample_size=5,
        forward_candles=[3, 6, 12],
        output_dir=output_dir,
        processed_dir=output_dir / "processed",
        research_dir=output_dir / "research",
        reports_dir=output_dir / "reports",
    )


def test_missing_ohlc_marks_missing_input_and_creates_dirs(tmp_path: Path):
    experiment_run = _run(tmp_path, tmp_path / "missing.csv")

    result = CalibrationExperimentRunner().run(experiment_run)

    assert result.status == "MISSING_INPUT"
    assert "OHLC file not found" in result.message
    assert experiment_run.processed_dir.exists()
    assert experiment_run.research_dir.exists()
    assert experiment_run.reports_dir.exists()


def test_completed_subprocess_sequence_marks_completed(tmp_path: Path, monkeypatch):
    ohlc_path = tmp_path / "ohlc.csv"
    ohlc_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")
    calls = []

    def fake_run(command, check, capture_output, text):
        calls.append(command)
        return CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("sqre.calibration_experiments.runner.subprocess.run", fake_run)

    result = CalibrationExperimentRunner().run(_run(tmp_path, ohlc_path))

    assert result.status == "COMPLETED"
    assert len(calls) == 6
    assert any("--minimum-sample-size" in command for command in calls)


def test_failed_subprocess_marks_failed(tmp_path: Path, monkeypatch):
    ohlc_path = tmp_path / "ohlc.csv"
    ohlc_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")

    def fake_run(command, check, capture_output, text):
        return CompletedProcess(command, 1, stdout="", stderr="boom")

    monkeypatch.setattr("sqre.calibration_experiments.runner.subprocess.run", fake_run)

    result = CalibrationExperimentRunner().run(_run(tmp_path, ohlc_path))

    assert result.status == "FAILED"
    assert "Event Detection failed with exit code 1" in result.message
    assert "boom" in result.message


def test_skip_existing_skips_completed_run(tmp_path: Path, monkeypatch):
    ohlc_path = tmp_path / "ohlc.csv"
    ohlc_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")
    experiment_run = _run(tmp_path, ohlc_path)
    experiment_run.reports_dir.mkdir(parents=True)
    (experiment_run.reports_dir / "price_outcome_research_report.txt").write_text("done", encoding="utf-8")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr("sqre.calibration_experiments.runner.subprocess.run", fail_if_called)

    result = CalibrationExperimentRunner().run(experiment_run, skip_existing=True)

    assert result.status == "SKIPPED"


def test_runner_does_not_raise_on_failure_without_strict(tmp_path: Path, monkeypatch):
    ohlc_path = tmp_path / "ohlc.csv"
    ohlc_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")

    def fake_run(command, check, capture_output, text):
        return CompletedProcess(command, 1, stdout="", stderr="boom")

    monkeypatch.setattr("sqre.calibration_experiments.runner.subprocess.run", fake_run)

    result = CalibrationExperimentRunner().run(_run(tmp_path, ohlc_path))

    assert result.status == "FAILED"
