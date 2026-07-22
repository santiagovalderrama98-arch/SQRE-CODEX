from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    PartialSampleReviewRow,
    PartialSensitivityComplementReviewRow,
    PartialStateComplementReviewRow,
    PartialTransitionComplementReviewRow,
)
from sqre.h4_partial_complementary_dispersion_review.partial_baseline_interpretation import (
    build_partial_baseline_interpretation,
)


def _sample(coverage: float = 0.5) -> PartialSampleReviewRow:
    return PartialSampleReviewRow(
        candidate_id="eurusd_h4_period_5_partial",
        sample_label="PARTIAL_SAMPLE",
        coverage_ratio=coverage,
        run_status="COMPLETED",
        sample_adequacy_class="PARTIAL_SAMPLE_RESEARCH_USABLE",
        partial_comparison_class="CONSISTENT_WITH_BASELINE_RANGE",
        condition_profile_count=48,
        partial_sample_status="PARTIAL_VALIDATED",
        partial_sample_diagnostic="ok",
    )


def _state() -> PartialStateComplementReviewRow:
    return PartialStateComplementReviewRow("c", "PARTIAL_SAMPLE", "DIVERSE", 3, "A", "B", "READY", "STATE_CONSISTENT_WITH_BASELINE", "ok")


def _transition() -> PartialTransitionComplementReviewRow:
    return PartialTransitionComplementReviewRow("c", "PARTIAL_SAMPLE", "A_TO_B", 3, "B", "READY", "TRANSITION_CONSISTENT_WITH_BASELINE", "ok")


def _sensitivity(value: str) -> PartialSensitivityComplementReviewRow:
    return PartialSensitivityComplementReviewRow("c", "PARTIAL_SAMPLE", "HIGH", 4, 0, "CONSISTENT_WITH_BASELINE_RANGE", 48, value, "ok")


def test_interpretation_matrix_classifies_support_correctly():
    row = build_partial_baseline_interpretation(
        _sample(),
        _state(),
        _transition(),
        _sensitivity("PARTIAL_REINFORCES_SCENARIO_SENSITIVITY"),
        H4PartialComplementaryDispersionReviewConfig(),
    )

    assert row.partial_baseline_interpretation_class == "COMPLEMENTARY_EVIDENCE_SUPPORTS_PRIOR_H4_FINDINGS"


def test_interpretation_matrix_classifies_consistent_but_limited_correctly():
    row = build_partial_baseline_interpretation(
        _sample(coverage=0.55),
        _state(),
        _transition(),
        _sensitivity("PARTIAL_CONSISTENT_WITH_BASELINE_RANGE"),
        H4PartialComplementaryDispersionReviewConfig(),
    )

    assert row.partial_baseline_interpretation_class == "COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED"
