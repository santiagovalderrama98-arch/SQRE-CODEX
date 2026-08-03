from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.models import ScenarioInventoryRow
from sqre.h4_timestamped_state_transition_outputs.state_output_normalizer import normalize_state_outputs
from sqre.h4_timestamped_state_transition_outputs.timestamped_output_discovery import TimestampedOutputSource


def test_state_normalizer_creates_normalized_h4_timestamped_state_rows(tmp_path: Path):
    path = tmp_path / "market_states.csv"
    path.write_text(
        "Scenario_ID,State_Time,Market_State,State_Confidence,Structure_ID,Timeframe\n"
        "SCN_1,2026-01-01 00:00:00,A,0.7,STR_1,H4\n",
        encoding="utf-8",
    )
    scenario = _scenario()
    source = TimestampedOutputSource(path, "TIMESTAMPED_STATE_SOURCE", "State_Time", 1)

    rows = normalize_state_outputs([source], [scenario], "EURUSD", "H4")

    assert len(rows) == 1
    assert rows[0].state_event_date == "2026-01-01"
    assert rows[0].market_state == "A"


def _scenario() -> ScenarioInventoryRow:
    return ScenarioInventoryRow(
        scenario_id="SCN_1",
        symbol="EURUSD",
        timeframe="H4",
        period_start="2026-01-01",
        period_end="2026-01-31",
        scenario_status="COMPLETED",
        expected_state_count=1,
        expected_transition_count=0,
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
