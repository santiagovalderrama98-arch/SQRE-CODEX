"""Pipeline orchestration for SQRE Phase 7.4.2 state threshold experiments."""

from __future__ import annotations

from pathlib import Path

from sqre.state_threshold_experiments.config import (
    build_experiment_runs,
    load_state_threshold_experiment_config,
)
from sqre.state_threshold_experiments.metrics import (
    apply_baseline_comparisons,
    collect_state_threshold_metrics,
)
from sqre.state_threshold_experiments.models import (
    StateThresholdExperimentMetricsRow,
    StateThresholdExperimentSummary,
)
from sqre.state_threshold_experiments.reports import (
    write_state_threshold_experiment_report,
    write_state_threshold_experiment_summary_csv,
)
from sqre.state_threshold_experiments.runner import StateThresholdExperimentRunner


def run_state_threshold_experiments(
    config_path: Path | str,
    output_dir: Path | str,
    summary_csv_path: Path | str,
    report_path: Path | str,
    profile_filter: str | None = None,
    scenario_filter: str | None = None,
    strict: bool = False,
    skip_existing: bool = False,
) -> StateThresholdExperimentSummary:
    config = load_state_threshold_experiment_config(config_path)
    runs = build_experiment_runs(
        config=config,
        output_dir=output_dir,
        profile_filter=profile_filter,
        scenario_filter=scenario_filter,
    )
    runner = StateThresholdExperimentRunner(pip_size=config.pip_size)
    rows: list[StateThresholdExperimentMetricsRow] = []
    for run in runs:
        result = runner.run(run, skip_existing=skip_existing)
        rows.append(collect_state_threshold_metrics(run, result))
        if strict and result.status != "COMPLETED":
            raise RuntimeError(f"{run.experiment_run_id} failed with status {result.status}: {result.message}")

    rows = apply_baseline_comparisons(rows)
    summary = StateThresholdExperimentSummary(
        experiment_name=config.experiment_name,
        runs_configured=len(runs),
        runs_completed=sum(1 for row in rows if row.status == "COMPLETED"),
        runs_missing_input=sum(1 for row in rows if row.status == "MISSING_INPUT"),
        runs_failed=sum(1 for row in rows if row.status == "FAILED"),
        summary_rows=len(rows),
        output_path=Path(summary_csv_path),
        report_path=Path(report_path),
    )
    write_state_threshold_experiment_summary_csv(summary.output_path, rows)
    write_state_threshold_experiment_report(summary.report_path, summary, rows)
    return summary
