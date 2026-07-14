"""Pipeline for M15 introduction review."""

from __future__ import annotations

from pathlib import Path

from sqre.m15_introduction_review.config import M15IntroductionReviewConfig
from sqre.m15_introduction_review.findings import build_m15_review_findings
from sqre.m15_introduction_review.loader import load_context_from_master_summary, load_m15_validation_summary
from sqre.m15_introduction_review.metrics import build_m15_review_rows
from sqre.m15_introduction_review.models import M15ReviewResult
from sqre.m15_introduction_review.reports import write_m15_review_report, write_m15_review_summary_csv


def run_m15_introduction_review(
    m15_summary_csv: Path | str,
    output_path: Path | str,
    report_path: Path | str,
    master_summary_csv: Path | str | None = None,
    config: M15IntroductionReviewConfig | None = None,
) -> M15ReviewResult:
    active_config = config or M15IntroductionReviewConfig()
    input_rows = load_m15_validation_summary(m15_summary_csv)
    context = load_context_from_master_summary(master_summary_csv)
    review_rows = build_m15_review_rows(input_rows, active_config, context)
    findings = build_m15_review_findings(review_rows)
    output = Path(output_path)
    report = Path(report_path)
    write_m15_review_summary_csv(output, review_rows)
    result = M15ReviewResult(
        input_summary=str(m15_summary_csv),
        master_summary=str(master_summary_csv or ""),
        rows_loaded=len(input_rows),
        scenarios_reviewed=sum(row.scenario_count for row in review_rows),
        output_path=output,
        report_path=report,
        rows=review_rows,
    )
    write_m15_review_report(report, result, findings)
    return result
