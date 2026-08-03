from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.source_inventory import build_source_inventory


def test_source_inventory_detects_existing_timestamped_state_and_transition_files(tmp_path: Path):
    validation = tmp_path / "validation"
    research = tmp_path / "research"
    scenario_dir = validation / "SCN_1"
    scenario_dir.mkdir(parents=True)
    research.mkdir()
    (scenario_dir / "market_states.csv").write_text(
        "Scenario_ID,State_Time,Market_State\nSCN_1,2026-01-01 00:00:00,A\n",
        encoding="utf-8",
    )
    (scenario_dir / "state_transitions.csv").write_text(
        "Scenario_ID,Transition_Time,Source_State,Target_State\nSCN_1,2026-01-01 04:00:00,A,B\n",
        encoding="utf-8",
    )
    config = H4TimestampedStateTransitionConfig(
        h4_d1_validation_dir=validation,
        h4_d1_structural_research_dir=research,
        validation_config=tmp_path / "missing.yaml",
    )

    rows = build_source_inventory(config)

    loaded = [row for row in rows if row.load_status == "LOADED"]
    assert any(row.source_type == "H4_TIMESTAMPED_STATE_SOURCE" for row in loaded)
    assert any(row.source_type == "H4_TIMESTAMPED_TRANSITION_SOURCE" for row in loaded)
