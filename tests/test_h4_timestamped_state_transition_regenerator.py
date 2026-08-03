from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.models import ScenarioInventoryRow
from sqre.h4_timestamped_state_transition_outputs.pipeline_regenerator import evaluate_regeneration_support


def test_regenerator_is_safely_skipped_when_raw_ohlc_is_missing(tmp_path):
    scenario = _scenario(raw_ohlc_file=str(tmp_path / "missing.csv"))

    rows = evaluate_regeneration_support([scenario], H4TimestampedStateTransitionConfig(output_dir=tmp_path / "out"))

    assert rows[0].attempted is True
    assert rows[0].status == "SKIPPED_RAW_OHLC_MISSING"


def test_regenerator_does_not_download_data(tmp_path):
    scenario = _scenario(raw_ohlc_file=str(tmp_path / "missing.csv"))

    evaluate_regeneration_support([scenario], H4TimestampedStateTransitionConfig(output_dir=tmp_path / "out"))

    assert not (tmp_path / "missing.csv").exists()


def _scenario(raw_ohlc_file: str) -> ScenarioInventoryRow:
    return ScenarioInventoryRow(
        scenario_id="SCN_1",
        symbol="EURUSD",
        timeframe="H4",
        period_start="2026-01-01",
        period_end="2026-01-31",
        scenario_status="COMPLETED",
        expected_state_count=0,
        expected_transition_count=0,
        raw_ohlc_file=raw_ohlc_file,
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
