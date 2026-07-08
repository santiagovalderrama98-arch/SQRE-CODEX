"""Multi-scenario validation runner for SQRE."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence

from sqre.validation.config import load_validation_config
from sqre.validation.metrics import collect_scenario_metrics, write_summary_csv
from sqre.validation.models import (
    COMPLETED,
    FAILED,
    MISSING_INPUT,
    SKIPPED,
    ScenarioMetrics,
    ScenarioRunResult,
    ValidationSummary,
)
from sqre.validation.reports import write_validation_report


CommandRunner = Callable[[Sequence[str], Path], subprocess.CompletedProcess[str]]


def run_multi_scenario_validation(
    *,
    config_path: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    summary_csv_path: Path | str,
    scenario_id: str | None = None,
    strict: bool = False,
    skip_existing: bool = False,
    command_runner: CommandRunner | None = None,
) -> tuple[ValidationSummary, list[ScenarioRunResult], list[ScenarioMetrics]]:
    config = load_validation_config(config_path, output_dir=output_dir, scenario_id=scenario_id)
    repo_root = Path(__file__).resolve().parents[2]
    runner = command_runner or _run_command

    results: list[ScenarioRunResult] = []
    metrics: list[ScenarioMetrics] = []

    for scenario in config.scenarios:
        result = _run_scenario(scenario, repo_root=repo_root, command_runner=runner, skip_existing=skip_existing)
        results.append(result)
        metrics.append(collect_scenario_metrics(scenario, result))
        if strict and result.status in {FAILED, MISSING_INPUT}:
            break

    summary = _build_summary(
        validation_name=config.validation_name,
        scenarios_configured=len(config.scenarios),
        scenarios_selected=len(config.scenarios),
        results=results,
        summary_csv_path=Path(summary_csv_path),
        report_path=Path(report_path),
    )
    write_summary_csv(summary.summary_csv_path, metrics)
    write_validation_report(summary.report_path, config=config, summary=summary, metrics=metrics)
    return summary, results, metrics


def _run_scenario(
    scenario,
    *,
    repo_root: Path,
    command_runner: CommandRunner,
    skip_existing: bool,
) -> ScenarioRunResult:
    final_output = scenario.research_dir / "price_outcomes.csv"
    if skip_existing and final_output.exists():
        return _result(scenario, SKIPPED, "Existing scenario output found")

    if not scenario.ohlc_path.exists():
        return _result(scenario, MISSING_INPUT, f"Missing input file: {scenario.ohlc_path}")

    scenario.processed_dir.mkdir(parents=True, exist_ok=True)
    scenario.research_dir.mkdir(parents=True, exist_ok=True)
    scenario.reports_dir.mkdir(parents=True, exist_ok=True)

    commands = _commands(scenario, repo_root)
    for label, command in commands:
        completed = command_runner(command, repo_root)
        if completed.returncode != 0:
            details = _failure_details(completed)
            return _result(scenario, FAILED, f"{label} failed with exit code {completed.returncode}: {details}")
    return _result(scenario, COMPLETED, "Scenario completed")


def _commands(scenario, repo_root: Path) -> list[tuple[str, list[str]]]:
    scripts = repo_root / "scripts"
    forward_windows = ",".join(str(item) for item in scenario.forward_candles)
    return [
        (
            "event_detection",
            [
                sys.executable,
                str(scripts / "run_event_detection.py"),
                "--input",
                str(scenario.ohlc_path),
                "--output-events",
                str(scenario.processed_dir / "events.csv"),
                "--output-report",
                str(scenario.reports_dir / "event_report.txt"),
                "--symbol",
                scenario.symbol,
                "--timeframe",
                scenario.timeframe,
            ],
        ),
        (
            "market_structure",
            [
                sys.executable,
                str(scripts / "run_market_structure.py"),
                "--events",
                str(scenario.processed_dir / "events.csv"),
                "--output-dir",
                str(scenario.processed_dir),
                "--report",
                str(scenario.reports_dir / "market_structure_report.txt"),
                "--max-structure-duration-seconds",
                str(scenario.max_structure_duration_seconds),
            ],
        ),
        (
            "market_states",
            [
                sys.executable,
                str(scripts / "run_market_states.py"),
                "--structures",
                str(scenario.processed_dir / "structures.csv"),
                "--output",
                str(scenario.processed_dir / "market_states.csv"),
                "--report",
                str(scenario.reports_dir / "market_states_report.txt"),
            ],
        ),
        (
            "transition_engine",
            [
                sys.executable,
                str(scripts / "run_transition_engine.py"),
                "--states",
                str(scenario.processed_dir / "market_states.csv"),
                "--output-dir",
                str(scenario.processed_dir),
                "--report",
                str(scenario.reports_dir / "transition_engine_report.txt"),
            ],
        ),
        (
            "research_engine",
            [
                sys.executable,
                str(scripts / "run_research_engine.py"),
                "--states",
                str(scenario.processed_dir / "market_states.csv"),
                "--transitions",
                str(scenario.processed_dir / "state_transitions.csv"),
                "--output-dir",
                str(scenario.research_dir),
                "--report",
                str(scenario.reports_dir / "research_engine_report.txt"),
                "--forward-windows",
                forward_windows,
                "--minimum-sample-size",
                str(scenario.minimum_sample_size),
            ],
        ),
        (
            "price_outcome_research",
            [
                sys.executable,
                str(scripts / "run_price_outcome_research.py"),
                "--states",
                str(scenario.processed_dir / "market_states.csv"),
                "--transitions",
                str(scenario.processed_dir / "state_transitions.csv"),
                "--ohlc",
                str(scenario.ohlc_path),
                "--output-dir",
                str(scenario.research_dir),
                "--report",
                str(scenario.reports_dir / "price_outcome_research_report.txt"),
                "--pip-size",
                str(scenario.pip_size),
                "--forward-candles",
                forward_windows,
                "--minimum-sample-size",
                str(scenario.minimum_sample_size),
            ],
        ),
    ]


def _run_command(command: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def _failure_details(completed: subprocess.CompletedProcess[str]) -> str:
    message = (completed.stderr or completed.stdout or "").strip()
    return message.splitlines()[-1] if message else "no command output"


def _result(scenario, status: str, message: str) -> ScenarioRunResult:
    return ScenarioRunResult(
        scenario_id=scenario.scenario_id,
        symbol=scenario.symbol,
        timeframe=scenario.timeframe,
        status=status,
        message=message,
        ohlc_path=scenario.ohlc_path,
        scenario_output_dir=scenario.scenario_output_dir,
        processed_dir=scenario.processed_dir,
        research_dir=scenario.research_dir,
        reports_dir=scenario.reports_dir,
    )


def _build_summary(
    *,
    validation_name: str,
    scenarios_configured: int,
    scenarios_selected: int,
    results: list[ScenarioRunResult],
    summary_csv_path: Path,
    report_path: Path,
) -> ValidationSummary:
    return ValidationSummary(
        validation_name=validation_name,
        scenarios_configured=scenarios_configured,
        scenarios_selected=scenarios_selected,
        scenarios_completed=_count(results, COMPLETED),
        scenarios_missing_input=_count(results, MISSING_INPUT),
        scenarios_failed=_count(results, FAILED),
        scenarios_skipped=_count(results, SKIPPED),
        summary_csv_path=summary_csv_path,
        report_path=report_path,
    )


def _count(results: list[ScenarioRunResult], status: str) -> int:
    return sum(1 for result in results if result.status == status)
