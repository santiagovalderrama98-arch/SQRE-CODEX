"""Pipeline for H1/M5 duration calibration review."""

from __future__ import annotations

from pathlib import Path

from sqre.timeframe_duration_calibration_review.config import TimeframeDurationCalibrationReviewConfig
from sqre.timeframe_duration_calibration_review.findings import build_duration_review_findings
from sqre.timeframe_duration_calibration_review.loader import load_duration_experiment_summary
from sqre.timeframe_duration_calibration_review.metrics import build_duration_review_rows
from sqre.timeframe_duration_calibration_review.models import DurationReviewResult
from sqre.timeframe_duration_calibration_review.reports import (
    write_duration_review_report,
    write_duration_review_summary_csv,
)


def run_timeframe_duration_calibration_review(
    experiment_summary_path: Path | str,
    output_path: Path | str,
    report_path: Path | str,
    config: TimeframeDurationCalibrationReviewConfig | None = None,
) -> DurationReviewResult:
    active_config = config or TimeframeDurationCalibrationReviewConfig()
    input_rows = load_duration_experiment_summary(experiment_summary_path)
    review_rows = build_duration_review_rows(input_rows, active_config)
    findings = build_duration_review_findings(review_rows)
    output = Path(output_path)
    report = Path(report_path)
    write_duration_review_summary_csv(output, review_rows)
    result = DurationReviewResult(
        input_experiment_summary=str(experiment_summary_path),
        rows_loaded=len(input_rows),
        timeframes_reviewed=len({row.timeframe for row in review_rows}),
        profiles_reviewed=len(review_rows),
        output_path=output,
        report_path=report,
        rows=review_rows,
    )
    write_duration_review_report(report, result, findings)
    return result
