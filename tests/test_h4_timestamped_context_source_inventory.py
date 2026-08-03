from pathlib import Path

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.source_inventory import build_source_inventory


def test_source_inventory_detects_timestamped_transition_files(tmp_path: Path):
    validation = tmp_path / "validation"
    scenario = validation / "scenario_a"
    scenario.mkdir(parents=True)
    (scenario / "state_transitions.csv").write_text(
        "Scenario_ID,Transition_Time,Source_State,Target_State,Transition_Label\n"
        "SCN_1,2026-01-01 04:00:00,A,B,A -> B\n",
        encoding="utf-8",
    )
    config = H4TimestampedContextTableGenerationConfig(
        h4_combined_context_dir=tmp_path / "combined",
        h4_d1_validation_dir=validation,
        h4_d1_structural_research_dir=tmp_path / "research",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out/report.txt",
    )

    rows = build_source_inventory(config)

    transition_rows = [row for row in rows if row.source_type == "H4_TIMESTAMPED_TRANSITION_SOURCE"]
    assert transition_rows
    assert transition_rows[0].timestamp_columns == "Transition_Time"
    assert "Source_State" in transition_rows[0].state_columns


def test_source_inventory_detects_timestamped_state_files(tmp_path: Path):
    research = tmp_path / "research" / "scenario_a"
    research.mkdir(parents=True)
    (research / "market_states.csv").write_text(
        "Scenario_ID,State_Time,Market_State\nSCN_1,2026-01-01 00:00:00,A\n",
        encoding="utf-8",
    )
    config = H4TimestampedContextTableGenerationConfig(
        h4_combined_context_dir=tmp_path / "combined",
        h4_d1_validation_dir=tmp_path / "validation",
        h4_d1_structural_research_dir=tmp_path / "research",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out/report.txt",
    )

    rows = build_source_inventory(config)

    state_rows = [row for row in rows if row.path.endswith("market_states.csv")]
    assert state_rows
    assert state_rows[0].timestamp_columns == "State_Time"
    assert state_rows[0].state_columns == "Market_State"
