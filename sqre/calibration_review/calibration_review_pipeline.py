"""Pipeline for SQRE Phase 7.4 calibration review."""

from __future__ import annotations

from pathlib import Path

from sqre.calibration_review.config import CalibrationReviewConfig
from sqre.calibration_review.findings import generate_calibration_findings
from sqre.calibration_review.loader import load_validation_summaries
from sqre.calibration_review.metrics import build_calibration_metrics
from sqre.calibration_review.models import CalibrationReviewSummary
from sqre.calibration_review.reports import (
    write_calibration_review_report,
    write_calibration_review_summary_csv,
)


def run_calibration_review(
    summary_csv_paths: list[Path | str],
    output_path: Path | str,
    report_path: Path | str,
    config: CalibrationReviewConfig | None = None,
) -> CalibrationReviewSummary:
    active_config = config or CalibrationReviewConfig()
    output = Path(output_path)
    report = Path(report_path)
    scenarios = load_validation_summaries(summary_csv_paths)
    rows = build_calibration_metrics(scenarios, active_config)
    findings = generate_calibration_findings(rows, active_config)
    summary = CalibrationReviewSummary(
        input_files=[str(path) for path in summary_csv_paths],
        scenarios_loaded=len(scenarios),
        completed_scenarios=sum(1 for scenario in scenarios if scenario.status == "COMPLETED"),
        missing_or_failed_scenarios=sum(1 for scenario in scenarios if scenario.status != "COMPLETED"),
        summary_rows=len(rows),
        finding_count=len(findings),
        review_status=_review_status(rows),
        output_path=output,
        report_path=report,
    )
    write_calibration_review_summary_csv(output, rows)
    write_calibration_review_report(report, summary, rows, findings)
    return summary


def _review_status(rows) -> str:
    statuses = {row.calibration_status for row in rows}
    if "REVIEW" in statuses:
        return "REVIEW"
    if "WATCH" in statuses:
        return "WATCH"
    if "NOT_AVAILABLE" in statuses:
        return "PARTIAL"
    return "OK"
