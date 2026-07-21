from pathlib import Path

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.feasibility_classifier import build_summary
from sqre.h4_expanded_sample_feasibility_review.models import (
    AvailabilityReviewRow,
    FeasibilityMatrixRow,
    H4ExpandedSampleFeasibilityResult,
    RawFileInventoryRow,
    SourceInventoryRow,
    ValidationCoverageRow,
)
from sqre.h4_expanded_sample_feasibility_review.reports import build_report_text, write_review_outputs


def test_write_review_outputs_creates_expected_csvs_and_report(tmp_path: Path):
    raw = [RawFileInventoryRow("x", "EURUSD_H4_period_1.csv", "NO", "EURUSD", "H4", 1, "a", "b", "KNOWN", "")]
    feasibility = [
        FeasibilityMatrixRow(
            "eurusd_h4_period_1",
            "EURUSD",
            "H4",
            "a",
            "b",
            "AVAILABLE_FULL",
            "NOT_VALIDATED",
            1.0,
            "PRESENT",
            "MISSING",
            "FEASIBLE_FULL_SAMPLE",
            "NO_MAJOR_CONSTRAINT_IDENTIFIED",
            "",
            "",
        )
    ]
    result = H4ExpandedSampleFeasibilityResult(
        tmp_path,
        tmp_path / "report.txt",
        source_inventory=[SourceInventoryRow("source", "csv", "x", "YES", "present_loaded", 1, 1, "")],
        raw_files=raw,
        availability_rows=[
            AvailabilityReviewRow("eurusd_h4_period_1", "EURUSD", "H4", "a", "b", "AVAILABLE_FULL", 1.0, "a", "b", "x", "NO", "")
        ],
        validation_rows=[
            ValidationCoverageRow("eurusd_h4_period_1", "EURUSD", "H4", "NOT_VALIDATED", 0, 0, 0, 0, "MISSING", "")
        ],
        feasibility_rows=feasibility,
        summary=build_summary(0, raw, feasibility),
    )

    write_review_outputs(result)

    assert (tmp_path / "h4_expansion_feasibility_matrix.csv").exists()
    assert (tmp_path / "h4_expanded_sample_feasibility_summary.csv").exists()
    assert result.report_path.exists()
    summary = pd.read_csv(tmp_path / "h4_expanded_sample_feasibility_summary.csv")
    assert summary.loc[0, "feasible_full_sample_count"] == 1


def test_report_text_has_required_sections_and_no_forbidden_execution_terms(tmp_path: Path):
    result = H4ExpandedSampleFeasibilityResult(tmp_path, tmp_path / "report.txt")

    text = build_report_text(result)

    assert "SQRE H4 Expanded Historical Sample Feasibility Review" in text
    assert "Research Readiness Assessment" in text
    assert "Limitations" in text
    lowered = text.lower()
    for term in ["buy", "sell", "entry", "exit", "take profit", "stop loss", "profitable"]:
        assert term not in lowered
