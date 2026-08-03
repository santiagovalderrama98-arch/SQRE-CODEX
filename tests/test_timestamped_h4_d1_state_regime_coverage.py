from sqre.timestamped_h4_d1_state_regime_generation.config import TimestampedH4D1StateRegimeGenerationConfig
from sqre.timestamped_h4_d1_state_regime_generation.coverage_review import build_coverage_review


def test_coverage_review_reports_available_outputs():
    row = build_coverage_review(
        h4_input_count=72,
        d1_input_count=30,
        h4_state_count=6,
        h4_transition_count=5,
        d1_state_count=6,
        config=TimestampedH4D1StateRegimeGenerationConfig(),
    )

    assert row.h4_state_coverage_class == "TIMESTAMPED_OUTPUT_AVAILABLE"
    assert row.h4_transition_coverage_class == "TIMESTAMPED_OUTPUT_AVAILABLE"
    assert row.d1_state_coverage_class == "TIMESTAMPED_OUTPUT_AVAILABLE"


def test_coverage_review_reports_missing_input():
    row = build_coverage_review(
        h4_input_count=0,
        d1_input_count=0,
        h4_state_count=0,
        h4_transition_count=0,
        d1_state_count=0,
        config=TimestampedH4D1StateRegimeGenerationConfig(),
    )

    assert row.h4_state_coverage_class == "INPUT_MISSING"
    assert row.d1_state_coverage_class == "INPUT_MISSING"
