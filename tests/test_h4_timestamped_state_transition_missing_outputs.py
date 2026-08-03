from sqre.h4_timestamped_state_transition_outputs.models import CoverageReviewRow
from sqre.h4_timestamped_state_transition_outputs.missing_output_review import build_missing_output_review


def test_missing_output_review_recommends_generating_state_transitions_with_timestamps():
    coverage = CoverageReviewRow(
        scenario_id="SCN_1",
        symbol="EURUSD",
        timeframe="H4",
        period_start="2026-01-01",
        period_end="2026-01-31",
        expected_state_count=2,
        expected_transition_count=1,
        timestamped_state_row_count=2,
        timestamped_transition_row_count=0,
        state_temporal_key_complete_row_count=2,
        transition_temporal_key_complete_row_count=0,
        state_coverage_ratio=1.0,
        transition_coverage_ratio=0.0,
        coverage_class="STATES_ONLY_TIMESTAMPED_COVERAGE",
        coverage_diagnostic="states only",
    )

    rows = build_missing_output_review([coverage])

    assert rows[0].required_source_action == "GENERATE_STATE_TRANSITIONS_WITH_TIMESTAMPS"
