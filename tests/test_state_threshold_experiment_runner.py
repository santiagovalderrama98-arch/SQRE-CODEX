from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from sqre.state_threshold_experiments.models import StateThresholdExperimentRun
from sqre.state_threshold_experiments.runner import StateThresholdExperimentRunner


def _run(tmp_path: Path, *, ohlc_exists: bool = True) -> StateThresholdExperimentRun:
    ohlc_path = tmp_path / "EURUSD_H4.csv"
    if ohlc_exists:
        ohlc_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")
    return StateThresholdExperimentRun(
        experiment_run_id="directional_stricter__eurusd_h4_period_1",
        profile_id="directional_stricter",
        scenario_id="eurusd_h4_period_1",
        symbol="EURUSD",
        timeframe="H4",
        ohlc_path=ohlc_path,
        state_config_path=Path("configs/validation/state_threshold_profiles.yaml"),
        max_structure_duration_seconds=604800,
        minimum_sample_size=5,
        forward_candles=[3, 6, 12],
        output_dir=tmp_path / "out",
        processed_dir=tmp_path / "out/processed",
        research_dir=tmp_path / "out/research",
        reports_dir=tmp_path / "out/reports",
    )


def test_runner_missing_input_returns_missing_input(tmp_path) -> None:
    result = StateThresholdExperimentRunner().run(_run(tmp_path, ohlc_exists=False))

    assert result.status == "MISSING_INPUT"
    assert "OHLC file not found" in result.message


def test_runner_executes_all_commands_with_state_profile(monkeypatch, tmp_path) -> None:
    calls: list[list[str]] = []

    def fake_run(command, check, capture_output, text):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = StateThresholdExperimentRunner().run(_run(tmp_path))

    assert result.status == "COMPLETED"
    assert len(calls) == 6
    market_states_command = calls[2]
    assert "scripts/run_market_states.py" in market_states_command
    assert "--state-config" in market_states_command
    assert "--state-profile" in market_states_command
    assert "directional_stricter" in market_states_command
    assert "--timeframe" in market_states_command
    assert "H4" in market_states_command


def test_runner_failed_step_returns_failed(monkeypatch, tmp_path) -> None:
    def fake_run(command, check, capture_output, text):
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = StateThresholdExperimentRunner().run(_run(tmp_path))

    assert result.status == "FAILED"
    assert "failed with exit code 1" in result.message


def test_runner_skip_existing_reuses_outputs(monkeypatch, tmp_path) -> None:
    experiment_run = _run(tmp_path)
    experiment_run.reports_dir.mkdir(parents=True)
    (experiment_run.reports_dir / "price_outcome_research_report.txt").write_text(
        f"created {datetime.now(timezone.utc).isoformat()}",
        encoding="utf-8",
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(subprocess, "run", fail_if_called)

    result = StateThresholdExperimentRunner().run(experiment_run, skip_existing=True)

    assert result.status == "SKIPPED"
