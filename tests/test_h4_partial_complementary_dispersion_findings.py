from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.findings import build_summary, potential_follow_up_areas
from sqre.h4_partial_complementary_dispersion_review.models import (
    PartialBaselineInterpretationRow,
    PartialSampleReviewRow,
)


def test_findings_build_summary_supports_complementary_review():
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

    summary = build_summary([sample], [interpretation], H4PartialComplementaryDispersionReviewConfig())

    assert summary.h4_partial_complementary_readiness_flag == "PARTIAL_SAMPLE_SUPPORTS_COMPLEMENTARY_H4_REVIEW"
    assert potential_follow_up_areas()
