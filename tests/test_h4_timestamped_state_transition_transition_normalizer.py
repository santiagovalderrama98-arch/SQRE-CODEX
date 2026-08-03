from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.models import ScenarioInventoryRow, TimestampedMarketStateRow
from sqre.h4_timestamped_state_transition_outputs.timestamped_output_discovery import TimestampedOutputSource
from sqre.h4_timestamped_state_transition_outputs.transition_output_normalizer import (
    build_transitions_from_states,
    normalize_transition_outputs,
)


def test_transition_normalizer_creates_normalized_h4_timestamped_transition_rows(tmp_path: Path):
    path = tmp_path / "state_transitions.csv"
    path.write_text(
        "Scenario_ID,Transition_Time,Source_State,Target_State,Transition_Label,Timeframe\n"
        "SCN_1,2026-01-01 04:00:00,A,B,A -> B,H4\n",
        encoding="utf-8",
    )
    source = TimestampedOutputSource(path, "TIMESTAMPED_TRANSITION_SOURCE", "Transition_Time", 1)

    rows = normalize_transition_outputs([source], [_scenario()], "EURUSD", "H4")

    assert len(rows) == 1
    assert rows[0].transition_label == "A -> B"
    assert rows[0].transition_date == "2026-01-01"


def test_transition_normalizer_builds_transitions_from_ordered_timestamped_states_only_when_safe():
    states = [_state("A", "2026-01-01 00:00:00"), _state("B", "2026-01-01 04:00:00")]

    rows = build_transitions_from_states(states)

    assert len(rows) == 1
    assert rows[0].transition_label == "A -> B"


def test_transition_normalizer_refuses_unordered_or_timestamp_missing_states():
    unordered = [_state("B", "2026-01-01 04:00:00"), _state("A", "2026-01-01 00:00:00")]
    missing = [_state("A", ""), _state("B", "2026-01-01 04:00:00")]

    assert build_transitions_from_states(unordered) == []
    assert build_transitions_from_states(missing) == []


def _scenario() -> ScenarioInventoryRow:
    return ScenarioInventoryRow(
        scenario_id="SCN_1",
        symbol="EURUSD",
        timeframe="H4",
        period_start="2026-01-01",
        period_end="2026-01-31",
        scenario_status="COMPLETED",
        expected_state_count=2,
        expected_transition_count=1,
        raw_ohlc_file="",
        raw_ohlc_available=False,
        existing_state_output_available=False,
        existing_transition_output_available=False,
        regeneration_attempted=False,
        regeneration_status="SKIPPED",
        timestamped_state_row_count=0,
        timestamped_transition_row_count=0,
        scenario_output_coverage_class="",
        scenario_diagnostic="",
    )


def _state(label: str, timestamp: str) -> TimestampedMarketStateRow:
    return TimestampedMarketStateRow(
        h4_timestamped_state_id=f"STATE_{label}",
        scenario_id="SCN_1",
        symbol="EURUSD",
        timeframe="H4",
        scenario_period_start="2026-01-01",
        scenario_period_end="2026-01-31",
        state_start_time=timestamp,
        state_end_time="",
        state_event_time=timestamp,
        state_event_date="2026-01-01" if timestamp else "",
        market_state=label,
        state_confidence="",
        structure_id="",
        structure_direction="",
        structural_efficiency="",
        structural_confidence="",
        state_row_source="test",
        state_row_diagnostic="test",
    )
