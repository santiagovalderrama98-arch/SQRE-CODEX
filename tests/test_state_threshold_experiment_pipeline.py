from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from sqre.state_threshold_experiments.models import StateThresholdExperimentRunResult
from sqre.state_threshold_experiments.state_threshold_experiment_pipeline import run_state_threshold_experiments
import sqre.state_threshold_experiments.state_threshold_experiment_pipeline as pipeline_module


def _write_config(path: Path, ohlc_path: Path) -> None:
    path.write_text(
        f"""
experiment_name: test_state_thresholds
symbol: EURUSD
pip_size: 0.0001
forward_candles: [3]
minimum_sample_size: 5
baseline_max_structure_duration_seconds:
  H4: 604800
state_config_path: configs/validation/state_threshold_profiles.yaml
base_scenarios:
  - scenario_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
    ohlc_path: {ohlc_path}
profiles:
  - state_baseline
  - directional_stricter
""",
        encoding="utf-8",
    )


class FakeRunner:
    def __init__(self, pip_size: float = 0.0001) -> None:
        self.pip_size = pip_size

    def run(self, experiment_run, *, skip_existing: bool = False):
        experiment_run.processed_dir.mkdir(parents=True)
        experiment_run.research_dir.mkdir(parents=True)
        pd.DataFrame({"Market_State": ["DIRECTIONAL_DISPLACEMENT"], "State_Confidence": [0.8]}).to_csv(
            experiment_run.processed_dir / "market_states.csv",
            index=False,
        )
        pd.DataFrame({"Condition_ID": ["C1"], "Low_Sample_Size": [False]}).to_csv(
            experiment_run.research_dir / "condition_summaries.csv",
            index=False,
        )
        return StateThresholdExperimentRunResult(
            experiment_run_id=experiment_run.experiment_run_id,
            profile_id=experiment_run.profile_id,
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
    def run(self, experiment_run, *, skip_existing: bool = False):
        return StateThresholdExperimentRunResult(
            experiment_run_id=experiment_run.experiment_run_id,
            profile_id=experiment_run.profile_id,
            scenario_id=experiment_run.scenario_id,
            symbol=experiment_run.symbol,
            timeframe=experiment_run.timeframe,
            status="FAILED",
            message="failure",
            started_at="2026-01-01T00:00:00+00:00",
            completed_at="2026-01-01T00:01:00+00:00",
            output_dir=experiment_run.output_dir,
        )


def test_state_threshold_experiment_pipeline_writes_outputs(monkeypatch, tmp_path) -> None:
    ohlc_path = tmp_path / "ohlc.csv"
    pd.DataFrame({"Date": ["2026-01-01"], "Open": [1], "High": [1], "Low": [1], "Close": [1]}).to_csv(
        ohlc_path,
        index=False,
    )
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, ohlc_path)
    monkeypatch.setattr(pipeline_module, "StateThresholdExperimentRunner", FakeRunner)

    summary = run_state_threshold_experiments(
        config_path=config_path,
        output_dir=tmp_path / "validation",
        summary_csv_path=tmp_path / "summary.csv",
        report_path=tmp_path / "report.txt",
    )

    assert summary.runs_configured == 2
    assert summary.runs_completed == 2
    assert summary.output_path.exists()
    assert summary.report_path.exists()


def test_state_threshold_experiment_pipeline_strict_raises(monkeypatch, tmp_path) -> None:
    ohlc_path = tmp_path / "ohlc.csv"
    pd.DataFrame({"Date": ["2026-01-01"], "Open": [1], "High": [1], "Low": [1], "Close": [1]}).to_csv(
        ohlc_path,
        index=False,
    )
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, ohlc_path)
    monkeypatch.setattr(pipeline_module, "StateThresholdExperimentRunner", FailingRunner)

    with pytest.raises(RuntimeError, match="failed with status FAILED"):
        run_state_threshold_experiments(
            config_path=config_path,
            output_dir=tmp_path / "validation",
            summary_csv_path=tmp_path / "summary.csv",
            report_path=tmp_path / "report.txt",
            strict=True,
        )
