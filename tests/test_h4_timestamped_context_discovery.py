from pathlib import Path

from sqre.h4_timestamped_context_table_generation.timestamped_source_discovery import discover_timestamped_sources


def test_discovery_finds_timestamped_transition_source(tmp_path: Path):
    source_dir = tmp_path / "scenario"
    source_dir.mkdir()
    (source_dir / "state_transitions.csv").write_text(
        "Scenario_ID,Event_Time,Source_State,Target_State\nSCN_1,2026-01-01 04:00:00,A,B\n",
        encoding="utf-8",
    )

    sources = discover_timestamped_sources([tmp_path])

    assert len(sources) == 1
    assert sources[0].source_type == "TIMESTAMPED_TRANSITION_SOURCE"
    assert sources[0].timestamp_column == "Event_Time"
