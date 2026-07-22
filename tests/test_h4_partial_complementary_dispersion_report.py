from pathlib import Path

from sqre.h4_partial_complementary_dispersion_review.findings import build_summary
from sqre.h4_partial_complementary_dispersion_review.models import (
    H4PartialComplementaryDispersionReviewResult,
    PartialBaselineInterpretationRow,
    PartialSampleReviewRow,
)
from sqre.h4_partial_complementary_dispersion_review.reports import (
    FORBIDDEN_REPORT_TERMS,
    build_report_text,
)


def test_report_includes_required_sections_and_excludes_blocked_language(tmp_path: Path):
    sample = PartialSampleReviewRow("c", "PARTIAL_SAMPLE", 0.5, "COMPLETED", "PARTIAL_SAMPLE_RESEARCH_USABLE", "CONSISTENT_WITH_BASELINE_RANGE", 48, "PARTIAL_VALIDATED", "ok")
    interpretation = PartialBaselineInterpretationRow(
        "c",
        "PARTIAL_SAMPLE",
        4,
        0.5,
        48,
        "PARTIAL_SAMPLE_RESEARCH_USABLE",
        "CONSISTENT_WITH_BASELINE_RANGE",
        "STATE_CONSISTENT_WITH_BASELINE",
        "TRANSITION_CONSISTENT_WITH_BASELINE",
        "PARTIAL_REINFORCES_SCENARIO_SENSITIVITY",
        "COMPLEMENTARY_EVIDENCE_SUPPORTS_PRIOR_H4_FINDINGS",
        "ok",
        "review",
    )
    result = H4PartialComplementaryDispersionReviewResult(
        partial_validation_dir=tmp_path,
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        partial_samples=[sample],
        interpretation_rows=[interpretation],
        summary=build_summary([], [interpretation], __import__(
            "sqre.h4_partial_complementary_dispersion_review.config",
            fromlist=["H4PartialComplementaryDispersionReviewConfig"],
        ).H4PartialComplementaryDispersionReviewConfig()),
    )

    text = build_report_text(result)

    assert "SQRE H4 Partial Sample Complementary Dispersion Review" in text
    assert "Partial Sample Caveat Review" in text
    lowered = text.lower()
    assert not [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
