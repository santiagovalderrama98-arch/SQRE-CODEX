from pathlib import Path

from sqre.h4_targeted_partial_expansion_validation.models import (
    H4TargetedPartialExpansionResult,
    H4TargetedPartialExpansionSummary,
)
from sqre.h4_targeted_partial_expansion_validation.reports import build_report_text


FORBIDDEN = [
    "buy",
    "sell",
    "entry",
    "exit",
    "trade signal",
    "trade setup",
    "take profit",
    "stop loss",
    "profitable",
    "opportunity",
    "edge",
    "best timeframe",
    "ranking",
    "should trade",
    "predicts",
    "optimal",
]


def test_report_sections_and_forbidden_words():
    result = H4TargetedPartialExpansionResult(
        feasibility_dir=Path("feasibility"),
        baseline_validation_dir=Path("baseline_validation"),
        baseline_research_dir=Path("baseline_research"),
        output_dir=Path("validation"),
        research_output_dir=Path("research"),
        report_path=Path("report.txt"),
        summary=H4TargetedPartialExpansionSummary(
            timeframe="H4",
            candidate_count=1,
            validated_partial_candidate_count=1,
            failed_candidate_count=0,
            partial_sample_count=1,
            baseline_scenario_count=4,
            average_coverage_ratio=0.6,
            partial_research_usable_count=1,
            partial_limited_count=0,
            partial_insufficient_count=0,
            partial_unavailable_count=0,
            h4_partial_expansion_profile="PARTIAL_EXPANSION_VALIDATED",
            h4_partial_expansion_readiness_flag="PARTIAL_SAMPLE_READY_FOR_COMPLEMENTARY_REVIEW",
            h4_partial_expansion_diagnostic="ok",
            recommended_follow_up="review",
        ),
    )

    text = build_report_text(result)
    lowered = text.lower()

    assert "SQRE H4 Targeted Partial Expansion Validation" in text
    assert "Sample Adequacy Review" in text
    for forbidden in FORBIDDEN:
        assert forbidden not in lowered
