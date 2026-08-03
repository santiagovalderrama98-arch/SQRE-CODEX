from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.timestamped_output_discovery import discover_timestamped_outputs


def test_discovery_finds_timestamped_state_and_transition_files(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "market_states.csv").write_text(
        "Scenario_ID,State_Time,Market_State\nSCN_1,2026-01-01 00:00:00,A\n",
        encoding="utf-8",
    )
    (root / "state_transitions.csv").write_text(
        "Scenario_ID,Transition_Time,Source_State,Target_State\nSCN_1,2026-01-01 04:00:00,A,B\n",
        encoding="utf-8",
    )

    sources = discover_timestamped_outputs([root])

    assert {source.source_type for source in sources} == {
        "TIMESTAMPED_STATE_SOURCE",
        "TIMESTAMPED_TRANSITION_SOURCE",
    }
