from pathlib import Path

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.models import ScenarioInventoryRow
from sqre.h4_timestamped_context_table_generation.timestamped_source_discovery import discover_timestamped_sources
from sqre.h4_timestamped_context_table_generation.transition_context_extractor import extract_timestamped_context_rows


def _scenario() -> ScenarioInventoryRow:
    return ScenarioInventoryRow(
        "SCN_1",
        "EURUSD",
        "H4",
        "2026-01-01",
        "2026-01-31",
        "raw.csv",
        "COMPLETED",
        3,
        2,
        False,
        False,
        0,
        "TIMESTAMPED_CONTEXT_MISSING",
        "",
    )


def test_extractor_creates_rows_from_transition_level_input(tmp_path: Path):
    (tmp_path / "state_transitions.csv").write_text(
        "Scenario_ID,Transition_Time,Source_State,Target_State,Transition_Label,Forward_Window\n"
        "SCN_1,2026-01-01 04:00:00,A,B,A -> B,12\n",
        encoding="utf-8",
    )
    sources = discover_timestamped_sources([tmp_path])

    rows, _, transition_ids = extract_timestamped_context_rows(
        sources,
        [_scenario()],
        H4TimestampedContextTableGenerationConfig(output_dir=tmp_path / "out", report_path=tmp_path / "out/report.txt"),
    )

    assert rows[0].h4_event_time == "2026-01-01 04:00:00"
    assert rows[0].h4_d1_alignment_date_key == "2026-01-01"
    assert rows[0].h4_transition_label == "A -> B"
    assert transition_ids == {"SCN_1"}


def test_extractor_does_not_fabricate_unordered_state_rows(tmp_path: Path):
    (tmp_path / "market_states.csv").write_text(
        "Scenario_ID,State_Time,Market_State\n"
        "SCN_1,2026-01-01 04:00:00,A\n"
        "SCN_1,2026-01-01 04:00:00,B\n",
        encoding="utf-8",
    )
    sources = discover_timestamped_sources([tmp_path])

    rows, state_ids, _ = extract_timestamped_context_rows(
        sources,
        [_scenario()],
        H4TimestampedContextTableGenerationConfig(output_dir=tmp_path / "out", report_path=tmp_path / "out/report.txt"),
    )

    assert rows == []
    assert state_ids == {"SCN_1"}
