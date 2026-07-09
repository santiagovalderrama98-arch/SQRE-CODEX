from pathlib import Path

import pandas as pd
import pytest

from sqre.calibration_experiments.calibration_experiment_pipeline import run_calibration_experiments
from sqre.calibration_experiments.models import ExperimentRunResult


def _write_config(path: Path, ohlc_path: Path) -> None:
    path.write_text(
        f"""
experiment_name: calibration_experiments_v1
symbol: EURUSD
pip_size: 0.0001
forward_candles: [3, 6, 12]
base_scenarios:
  - scenario_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
    ohlc_path: {ohlc_path}
duration_experiments:
  - experiment_id: duration_baseline
    max_structure_duration_seconds:
      H4: 604800
sample_size_experiments:
  - experiment_id: sample_size_5
    minimum_sample_size: 5
""",
        encoding="utf-8",
    )


class FakeRunner:
    def __init__(self, pip_size: float):
        self.pip_size = pip_size

    def run(self, experiment_run, *, skip_existing=False):
        experiment_run.ohlc_path.write_text("Date,Open,High,Low,Close,Volume\n2026-01-01,1,1,1,1,0\n", encoding="utf-8")
        experiment_run.processed_dir.mkdir(parents=True, exist_ok=True)
        experiment_run.research_dir.mkdir(parents=True, exist_ok=True)
        return ExperimentRunResult(
            experiment_run_id=experiment_run.experiment_run_id,
            experiment_type=experiment_run.experiment_type,
            experiment_id=experiment_run.experiment_id,
            scenario_id=experiment_run.scenario_id,
            symbol=experiment_run.symbol,
            timeframe=experiment_run.timeframe,
            status="COMPLETED",
            message="Completed successfully",
            started_at="2026-01-01T00:00:00+00:00",
            completed_at="2026-01-01T00:01:00+00:00",
            output_dir=experiment_run.output_dir,
        )


class FailingRunner(FakeRunner):
    def run(self, experiment_run, *, skip_existing=False):
        return ExperimentRunResult(
            experiment_run_id=experiment_run.experiment_run_id,
            experiment_type=experiment_run.experiment_type,
            experiment_id=experiment_run.experiment_id,
            scenario_id=experiment_run.scenario_id,
            symbol=experiment_run.symbol,
            timeframe=experiment_run.timeframe,
            status="FAILED",
            message="synthetic failure",
            started_at="2026-01-01T00:00:00+00:00",
            completed_at="2026-01-01T00:01:00+00:00",
            output_dir=experiment_run.output_dir,
        )


def test_run_calibration_experiments_with_mocked_runner(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    summary_csv = tmp_path / "summary.csv"
    report = tmp_path / "report.txt"
    _write_config(config_path, tmp_path / "ohlc.csv")
    monkeypatch.setattr(
        "sqre.calibration_experiments.calibration_experiment_pipeline.CalibrationExperimentRunner",
        FakeRunner,
    )

    summary = run_calibration_experiments(config_path, tmp_path / "out", summary_csv, report)

    assert summary.runs_configured == 2
    assert summary.runs_completed == 2
    assert summary.summary_rows == 2
    assert summary_csv.exists()
    assert report.exists()
    assert len(pd.read_csv(summary_csv)) == 2


def test_run_calibration_experiments_filters_work(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    summary_csv = tmp_path / "summary.csv"
    report = tmp_path / "report.txt"
    _write_config(config_path, tmp_path / "ohlc.csv")
    monkeypatch.setattr(
        "sqre.calibration_experiments.calibration_experiment_pipeline.CalibrationExperimentRunner",
        FakeRunner,
    )

    summary = run_calibration_experiments(
        config_path,
        tmp_path / "out",
        summary_csv,
        report,
        experiment_type_filter="DURATION",
    )

    frame = pd.read_csv(summary_csv)
    assert summary.runs_configured == 1
    assert frame["Experiment_Type"].tolist() == ["DURATION"]


def test_run_calibration_experiments_strict_stops_on_failure(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, tmp_path / "ohlc.csv")
    monkeypatch.setattr(
        "sqre.calibration_experiments.calibration_experiment_pipeline.CalibrationExperimentRunner",
        FailingRunner,
    )

    with pytest.raises(RuntimeError, match="FAILED"):
        run_calibration_experiments(
            config_path,
            tmp_path / "out",
            tmp_path / "summary.csv",
            tmp_path / "report.txt",
            strict=True,
        )
