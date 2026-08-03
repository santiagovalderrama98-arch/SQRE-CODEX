import pandas as pd

from sqre.h4_d1_same_time_alignment_table.d1_context_index import D1ContextIndex
from sqre.h4_d1_same_time_alignment_table.h4_state_alignment_builder import (
    STATE_ALIGNMENT_COLUMNS,
    build_h4_state_alignment,
)
from tests.h4_d1_same_time_alignment_test_utils import candle_map, d1_states, h4_states


def test_state_builder_aligns_h4_state_to_d1_interval():
    rows = build_h4_state_alignment(
        h4_states(),
        D1ContextIndex(d1_states(), candle_map()),
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
    )

    assert list(rows.columns) == STATE_ALIGNMENT_COLUMNS
    assert rows["Alignment_Method"].iloc[0] == "D1_INTERVAL_CONTAINMENT_MATCH"
    assert rows["D1_State_ID"].iloc[0] == "D1_STATE_000001"


def test_state_builder_marks_unmatched_safely():
    states = h4_states().head(1).copy()
    states["State_Event_Time"] = "2026-08-01 04:00:00"
    states["State_Event_Date"] = "2026-08-01"

    rows = build_h4_state_alignment(
        states,
        D1ContextIndex(d1_states(), pd.DataFrame()),
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
    )

    assert rows["Alignment_Method"].iloc[0] == "NO_D1_SAME_TIME_MATCH"
    assert rows["D1_State_ID"].iloc[0] == ""
