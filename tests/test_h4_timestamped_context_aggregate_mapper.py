from pathlib import Path

from sqre.h4_timestamped_context_table_generation.aggregate_context_mapper import map_aggregate_contexts
from sqre.h4_timestamped_context_table_generation.models import TimestampedContextRow


def _row(transition_label: str = "A -> B") -> TimestampedContextRow:
    return TimestampedContextRow(
        "H4_TS_CTX_000001",
        "",
        "EURUSD",
        "H4",
        "SCN_1",
        "2026-01-01",
        "2026-01-31",
        "2026-01-01 04:00:00",
        "2026-01-01",
        "A",
        "B",
        transition_label,
        "12",
        "EXACT_EVENT_TIMESTAMP",
        "2026-01-01",
        "NO_AGGREGATE_CONTEXT_MATCH",
        "NO_CONTEXT_MATCH",
        "",
    )


def test_aggregate_mapper_matches_transition_label_and_forward_window(tmp_path: Path):
    combined = tmp_path / "combined"
    combined.mkdir()
    (combined / "h4_transition_state_context_inventory.csv").write_text(
        "Context_ID,Transition_Label,Forward_Window,Source_State,Target_State\nCTX_1,A -> B,12,A,B\n",
        encoding="utf-8",
    )

    rows = map_aggregate_contexts([_row()], combined)

    assert rows[0].aggregate_context_id == "CTX_1"
    assert rows[0].aggregate_context_match_method == "TRANSITION_LABEL_FORWARD_WINDOW_MATCH"


def test_aggregate_mapper_matches_state_pair_and_forward_window(tmp_path: Path):
    combined = tmp_path / "combined"
    combined.mkdir()
    (combined / "h4_transition_state_context_inventory.csv").write_text(
        "Context_ID,Forward_Window,Source_State,Target_State\nCTX_2,12,A,B\n",
        encoding="utf-8",
    )

    rows = map_aggregate_contexts([_row("")], combined)

    assert rows[0].aggregate_context_id == "CTX_2"
    assert rows[0].aggregate_context_match_method == "STATE_PAIR_FORWARD_WINDOW_MATCH"
