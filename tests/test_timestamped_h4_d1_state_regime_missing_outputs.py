from sqre.timestamped_h4_d1_state_regime_generation.config import TimestampedH4D1StateRegimeGenerationConfig
from sqre.timestamped_h4_d1_state_regime_generation.coverage_review import build_coverage_review
from sqre.timestamped_h4_d1_state_regime_generation.missing_output_review import build_missing_output_review


def test_missing_output_review_reports_no_action_when_outputs_exist():
    coverage = build_coverage_review(
        h4_input_count=72,
        d1_input_count=30,
        h4_state_count=6,
        h4_transition_count=5,
        d1_state_count=6,
        config=TimestampedH4D1StateRegimeGenerationConfig(),
    )

    rows = build_missing_output_review(coverage)

    assert len(rows) == 1
    assert rows[0].required_source_action == "NO_ACTION_REQUIRED"


def test_missing_output_review_reports_input_completeness():
    coverage = build_coverage_review(
        h4_input_count=0,
        d1_input_count=0,
        h4_state_count=0,
        h4_transition_count=0,
        d1_state_count=0,
        config=TimestampedH4D1StateRegimeGenerationConfig(),
    )

    rows = build_missing_output_review(coverage)

    assert rows[0].required_source_action == "REVIEW_SYNCHRONIZED_INPUT_COMPLETENESS"
