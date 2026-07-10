"""Subprocess runner for SQRE state threshold experiments."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqre.state_threshold_experiments.models import StateThresholdExperimentRun, StateThresholdExperimentRunResult


FINAL_REPORT_NAME = "price_outcome_research_report.txt"


class StateThresholdExperimentRunner:
    """Run one state threshold experiment through the existing SQRE CLIs."""

    def __init__(self, pip_size: float = 0.0001) -> None:
        self.pip_size = pip_size

    def run(
        self,
        experiment_run: StateThresholdExperimentRun,
        *,
        skip_existing: bool = False,
    ) -> StateThresholdExperimentRunResult:
        started_at = _now()
        _create_output_dirs(experiment_run)
        if not experiment_run.ohlc_path.exists():
            return _result(
                experiment_run,
                "MISSING_INPUT",
                f"OHLC file not found: {experiment_run.ohlc_path}",
                started_at,
            )
        if skip_existing and _final_report_path(experiment_run).exists():
            return _result(experiment_run, "SKIPPED", "Existing experiment output detected; execution skipped.", started_at)

        for step_name, command in _commands(experiment_run, pip_size=self.pip_size):
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
            if completed.returncode != 0:
                return _result(experiment_run, "FAILED", _failure_message(step_name, completed), started_at)
        return _result(experiment_run, "COMPLETED", "Completed successfully", started_at)


def _commands(experiment_run: StateThresholdExperimentRun, *, pip_size: float) -> list[tuple[str, list[str]]]:
    processed = experiment_run.processed_dir
    research = experiment_run.research_dir
    reports = experiment_run.reports_dir
    forward_values = ",".join(str(item) for item in experiment_run.forward_candles)
    return [
        (
            "Event Detection",
            [
                sys.executable,
                "scripts/run_event_detection.py",
                "--input",
                str(experiment_run.ohlc_path),
                "--output-events",
                str(processed / "events.csv"),
                "--output-report",
                str(reports / "event_report.txt"),
                "--symbol",
                experiment_run.symbol,
                "--timeframe",
                experiment_run.timeframe,
            ],
        ),
        (
            "Market Structure",
            [
                sys.executable,
                "scripts/run_market_structure.py",
                "--events",
                str(processed / "events.csv"),
                "--output-dir",
                str(processed),
                "--report",
                str(reports / "market_structure_report.txt"),
                "--max-structure-duration-seconds",
                str(experiment_run.max_structure_duration_seconds),
            ],
        ),
        (
            "Market States",
            [
                sys.executable,
                "scripts/run_market_states.py",
                "--structures",
                str(processed / "structures.csv"),
                "--output",
                str(processed / "market_states.csv"),
                "--report",
                str(reports / "market_states_report.txt"),
                "--state-config",
                str(experiment_run.state_config_path),
                "--state-profile",
                experiment_run.profile_id,
                "--timeframe",
                experiment_run.timeframe,
            ],
        ),
        (
            "Transition Engine",
            [
                sys.executable,
                "scripts/run_transition_engine.py",
                "--states",
                str(processed / "market_states.csv"),
                "--output-dir",
                str(processed),
                "--report",
                str(reports / "transition_engine_report.txt"),
            ],
        ),
        (
            "Research Engine",
            [
                sys.executable,
                "scripts/run_research_engine.py",
                "--states",
                str(processed / "market_states.csv"),
                "--transitions",
                str(processed / "state_transitions.csv"),
                "--output-dir",
                str(research),
                "--report",
                str(reports / "research_engine_report.txt"),
                "--forward-windows",
                forward_values,
                "--minimum-sample-size",
                str(experiment_run.minimum_sample_size),
            ],
        ),
        (
            "Price Outcome Research",
            [
                sys.executable,
                "scripts/run_price_outcome_research.py",
                "--states",
                str(processed / "market_states.csv"),
                "--transitions",
                str(processed / "state_transitions.csv"),
                "--ohlc",
                str(experiment_run.ohlc_path),
                "--output-dir",
                str(research),
                "--report",
                str(reports / FINAL_REPORT_NAME),
                "--pip-size",
                str(pip_size),
                "--forward-candles",
                forward_values,
                "--minimum-sample-size",
                str(experiment_run.minimum_sample_size),
            ],
        ),
    ]


def _create_output_dirs(experiment_run: StateThresholdExperimentRun) -> None:
    experiment_run.processed_dir.mkdir(parents=True, exist_ok=True)
    experiment_run.research_dir.mkdir(parents=True, exist_ok=True)
    experiment_run.reports_dir.mkdir(parents=True, exist_ok=True)


def _final_report_path(experiment_run: StateThresholdExperimentRun) -> Path:
    return experiment_run.reports_dir / FINAL_REPORT_NAME


def _failure_message(step_name: str, completed: subprocess.CompletedProcess[str]) -> str:
    detail = (completed.stderr or completed.stdout or "").strip()
    if len(detail) > 800:
        detail = detail[:800] + "..."
    return f"{step_name} failed with exit code {completed.returncode}: {detail}"


def _result(
    experiment_run: StateThresholdExperimentRun,
    status: str,
    message: str,
    started_at: str,
) -> StateThresholdExperimentRunResult:
    return StateThresholdExperimentRunResult(
        experiment_run_id=experiment_run.experiment_run_id,
        profile_id=experiment_run.profile_id,
        scenario_id=experiment_run.scenario_id,
        symbol=experiment_run.symbol,
        timeframe=experiment_run.timeframe,
        status=status,
        message=message,
        started_at=started_at,
        completed_at=_now(),
        output_dir=experiment_run.output_dir,
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
