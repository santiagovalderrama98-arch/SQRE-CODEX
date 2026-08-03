from sqre.timestamped_h4_d1_state_regime_generation.config import TimestampedH4D1StateRegimeGenerationConfig
from sqre.timestamped_h4_d1_state_regime_generation.coverage_review import build_coverage_review
from sqre.timestamped_h4_d1_state_regime_generation.findings import (
    build_summary,
    do_not_change_yet_lines,
    potential_follow_up_areas,
)


def test_findings_ready_summary_when_outputs_available():
    coverage = build_coverage_review(
        h4_input_count=72,
        d1_input_count=30,
        h4_state_count=6,
        h4_transition_count=5,
        d1_state_count=6,
        config=TimestampedH4D1StateRegimeGenerationConfig(),
    )

    summary = build_summary(coverage)

    assert summary.timestamped_h4_d1_state_regime_readiness_flag == "READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE"
    assert "H4/D1 same-time alignment table" in potential_follow_up_areas()
    assert "No Decision Engine was added." in do_not_change_yet_lines()


def test_findings_input_missing_summary():
    coverage = build_coverage_review(
        h4_input_count=0,
        d1_input_count=0,
        h4_state_count=0,
        h4_transition_count=0,
        d1_state_count=0,
        config=TimestampedH4D1StateRegimeGenerationConfig(),
    )

    summary = build_summary(coverage)

    assert summary.timestamped_h4_d1_state_regime_readiness_flag == "INPUT_COMPLETENESS_REVIEW_REQUIRED"
