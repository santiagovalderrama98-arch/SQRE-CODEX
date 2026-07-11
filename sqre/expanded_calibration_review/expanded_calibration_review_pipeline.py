"""Pipeline for SQRE Phase 7.4.4 expanded historical calibration review."""

from __future__ import annotations

from pathlib import Path

from sqre.expanded_calibration_review.config import ExpandedCalibrationReviewConfig
from sqre.expanded_calibration_review.findings import generate_expanded_calibration_findings
from sqre.expanded_calibration_review.loader import load_expanded_summaries
from sqre.expanded_calibration_review.metrics import build_timeframe_metrics
from sqre.expanded_calibration_review.models import ExpandedCalibrationReviewSummary
from sqre.expanded_calibration_review.reports import (
    write_expanded_calibration_review_report,
    write_expanded_calibration_review_summary_csv,
)


def run_expanded_calibration_review(
    summary_csv_paths: list[Path | str],
    output_path: Path | str,
    report_path: Path | str,
    config: ExpandedCalibrationReviewConfig | None = None,
) -> ExpandedCalibrationReviewSummary:
    active_config = config or ExpandedCalibrationReviewConfig()
    output = Path(output_path)
    report = Path(report_path)
    scenarios = load_expanded_summaries(summary_csv_paths)
    rows = build_timeframe_metrics(scenarios, active_config)
    findings = generate_expanded_calibration_findings(rows, active_config)
    summary = ExpandedCalibrationReviewSummary(
        input_files=[str(path) for path in summary_csv_paths],
        rows_loaded=len(scenarios),
        timeframes_reviewed=len(rows),
        summary_rows=len(rows),
        output_path=output,
        report_path=report,
    )
    write_expanded_calibration_review_summary_csv(output, rows)
    write_expanded_calibration_review_report(report, summary, rows, findings)
    return summary
