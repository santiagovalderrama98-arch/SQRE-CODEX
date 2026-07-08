"""Pipeline orchestration for SQRE Phase 7.4.1 calibration experiments."""

from __future__ import annotations

from pathlib import Path

from sqre.calibration_experiments.config import build_experiment_runs, load_calibration_experiment_config
from sqre.calibration_experiments.metrics import apply_baseline_comparisons, collect_experiment_metrics
from sqre.calibration_experiments.models import CalibrationExperimentSummary, ExperimentMetricsRow
from sqre.calibration_experiments.reports import (
    write_calibration_experiment_report,
    write_calibration_experiment_summary_csv,
)
from sqre.calibration_experiments.runner import CalibrationExperimentRunner


def run_calibration_experiments(
    config_path: Path | str,
    output_dir: Path | str,
    summary_csv_path: Path | str,
    report_path: Path | str,
    experiment_filter: str | None = None,
    experiment_type_filter: str | None = None,
    scenario_filter: str | None = None,
    strict: bool = False,
    skip_existing: bool = False,
) -> CalibrationExperimentSummary:
    config = load_calibration_experiment_config(config_path)
    runs = build_experiment_runs(
        config=config,
        output_dir=output_dir,
        experiment_filter=experiment_filter,
        experiment_type_filter=experiment_type_filter,
        scenario_filter=scenario_filter,
    )
    runner = CalibrationExperimentRunner(pip_size=config.pip_size)
    rows: list[ExperimentMetricsRow] = []
    for run in runs:
        result = runner.run(run, skip_existing=skip_existing)
        rows.append(collect_experiment_metrics(run, result))
        if strict and result.status != "COMPLETED":
            raise RuntimeError(f"{run.experiment_run_id} failed with status {result.status}: {result.message}")

    rows = apply_baseline_comparisons(rows)
    summary = CalibrationExperimentSummary(
        experiment_name=config.experiment_name,
        runs_configured=len(runs),
        runs_completed=sum(1 for row in rows if row.status == "COMPLETED"),
        runs_missing_input=sum(1 for row in rows if row.status == "MISSING_INPUT"),
        runs_failed=sum(1 for row in rows if row.status == "FAILED"),
        summary_rows=len(rows),
        output_path=Path(summary_csv_path),
        report_path=Path(report_path),
    )
    write_calibration_experiment_summary_csv(summary.output_path, rows)
    write_calibration_experiment_report(summary.report_path, summary, rows)
    return summary
