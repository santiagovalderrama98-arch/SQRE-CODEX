from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.models import (
    ScenarioInventoryRow,
    TimestampedMarketStateRow,
    TimestampedStateTransitionRow,
)
from sqre.h4_timestamped_state_transition_outputs.output_coverage_review import build_coverage_review


def test_coverage_review_classifies_full_coverage(tmp_path):
    scenario = _scenario(expected_states=1, expected_transitions=1)
    coverage = build_coverage_review([scenario], [_state()], [_transition()], H4TimestampedStateTransitionConfig(output_dir=tmp_path))

    assert coverage[0].coverage_class == "FULL_TIMESTAMPED_STATE_TRANSITION_COVERAGE"


def test_coverage_review_classifies_missing_coverage(tmp_path):
    scenario = _scenario(expected_states=1, expected_transitions=1)
    coverage = build_coverage_review([scenario], [], [], H4TimestampedStateTransitionConfig(output_dir=tmp_path))

    assert coverage[0].coverage_class == "NO_TIMESTAMPED_STATE_TRANSITION_COVERAGE"


def _scenario(expected_states: int, expected_transitions: int) -> ScenarioInventoryRow:
    return ScenarioInventoryRow(
        scenario_id="SCN_1",
        symbol="EURUSD",
        timeframe="H4",
        period_start="2026-01-01",
        period_end="2026-01-31",
        scenario_status="COMPLETED",
        expected_state_count=expected_states,
        expected_transition_count=expected_transitions,
        raw_ohlc_file="",
        raw_ohlc_available=False,
        existing_state_output_available=False,
        existing_transition_output_available=False,
        regeneration_attempted=False,
        regeneration_status="",
        timestamped_state_row_count=0,
        timestamped_transition_row_count=0,
        scenario_output_coverage_class="",
        scenario_diagnostic="",
    )


def _state() -> TimestampedMarketStateRow:
    return TimestampedMarketStateRow(
        "STATE_1",
        "SCN_1",
        "EURUSD",
        "H4",
        "2026-01-01",
        "2026-01-31",
        "2026-01-01 00:00:00",
        "",
        "2026-01-01 00:00:00",
        "2026-01-01",
        "A",
        "",
        "",
        "",
        "",
        "",
        "test",
        "test",
    )


def _transition() -> TimestampedStateTransitionRow:
    return TimestampedStateTransitionRow(
        "TR_1",
        "SCN_1",
        "EURUSD",
        "H4",
        "2026-01-01",
        "2026-01-31",
        "2026-01-01 04:00:00",
        "2026-01-01",
        "A",
        "B",
        "A -> B",
        "",
        "",
        "",
        "",
        "",
        "",
        "test",
        "test",
    )
