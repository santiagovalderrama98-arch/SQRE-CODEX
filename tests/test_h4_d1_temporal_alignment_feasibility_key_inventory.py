from pathlib import Path

from sqre.h4_d1_temporal_alignment_feasibility_review.models import SourceInventoryRow
from sqre.h4_d1_temporal_alignment_feasibility_review.temporal_key_inventory import build_temporal_key_inventory


def test_key_inventory_detects_exact_timestamp_columns(tmp_path: Path):
    path = tmp_path / "source.csv"
    path.write_text("Timestamp,Value\n2026-01-01 00:00:00,1\n", encoding="utf-8")

    row = _key(path)

    assert row.temporal_key_status == "EXACT_TIMESTAMP_KEYS_AVAILABLE"
    assert row.timestamp_columns == "Timestamp"


def test_key_inventory_detects_start_end_interval_columns(tmp_path: Path):
    path = tmp_path / "source.csv"
    path.write_text("Start_Time,End_Time,Value\n2026-01-01,2026-01-02,1\n", encoding="utf-8")

    row = _key(path)

    assert row.temporal_key_status == "START_END_TIME_KEYS_AVAILABLE"
    assert row.start_time_columns == "Start_Time"
    assert row.end_time_columns == "End_Time"


def test_key_inventory_detects_scenario_period_columns(tmp_path: Path):
    path = tmp_path / "source.csv"
    path.write_text("Scenario_ID,Period_Start,Period_End\nS1,2026-01-01,2026-01-02\n", encoding="utf-8")

    row = _key(path)

    assert row.temporal_key_status == "SCENARIO_PERIOD_KEYS_AVAILABLE"
    assert row.scenario_id_columns == "Scenario_ID"


def test_key_inventory_classifies_condition_only_h4_context(tmp_path: Path):
    path = tmp_path / "h4.csv"
    path.write_text(
        "Context_ID,Source_State,Target_State,Transition_Label,Forward_Window\n"
        "CTX_1,EXPANSION,CONSOLIDATION,EXPANSION -> CONSOLIDATION,12\n",
        encoding="utf-8",
    )

    row = _key(path, source_type="H4_COMBINED_CONTEXT")

    assert row.temporal_key_status == "CONDITION_ONLY_KEYS_AVAILABLE"
    assert "Transition_Label" in row.condition_only_columns
    assert "not same-time temporal alignment" in row.temporal_key_diagnostic


def _key(path: Path, source_type: str = "H4_COMBINED_CONTEXT"):
    source = SourceInventoryRow("source", source_type, str(path), True, "LOADED", 1, "loaded")
    return build_temporal_key_inventory([source])[0]
