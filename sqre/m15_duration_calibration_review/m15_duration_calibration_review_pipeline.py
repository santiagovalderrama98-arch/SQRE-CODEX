"""Pipeline for M15 duration calibration review."""

from __future__ import annotations

from pathlib import Path

from sqre.m15_duration_calibration_review.config import M15DurationCalibrationReviewConfig
from sqre.m15_duration_calibration_review.findings import build_m15_duration_review_findings
from sqre.m15_duration_calibration_review.loader import load_m15_duration_experiment_summary
from sqre.m15_duration_calibration_review.metrics import build_m15_duration_review_rows
from sqre.m15_duration_calibration_review.models import M15DurationReviewResult
from sqre.m15_duration_calibration_review.reports import (
    write_m15_duration_review_report,
    write_m15_duration_review_summary_csv,
)


def run_m15_duration_calibration_review(
    experiment_summary_path: Path | str,
    output_path: Path | str,
    report_path: Path | str,
    config: M15DurationCalibrationReviewConfig | None = None,
) -> M15DurationReviewResult:
    active_config = config or M15DurationCalibrationReviewConfig()
    input_rows = load_m15_duration_experiment_summary(experiment_summary_path)
    review_rows = build_m15_duration_review_rows(input_rows, active_config)
    findings = build_m15_duration_review_findings(review_rows)
    output = Path(output_path)
    report = Path(report_path)
    write_m15_duration_review_summary_csv(output, review_rows)
    result = M15DurationReviewResult(
        input_experiment_summary=str(experiment_summary_path),
        rows_loaded=len(input_rows),
        profiles_reviewed=len(review_rows),
        output_path=output,
        report_path=report,
        rows=review_rows,
    )
    write_m15_duration_review_report(report, result, findings)
    return result
