import pandas as pd

from sqre.h4_d1_same_time_alignment_table.d1_context_index import D1ContextIndex
from sqre.h4_d1_same_time_alignment_table.h4_transition_alignment_builder import (
    TRANSITION_ALIGNMENT_COLUMNS,
    build_h4_transition_alignment,
)
from tests.h4_d1_same_time_alignment_test_utils import candle_map, d1_states, h4_transitions


def test_transition_builder_aligns_h4_transition_to_d1_interval():
    rows = build_h4_transition_alignment(
        h4_transitions(),
        D1ContextIndex(d1_states(), candle_map()),
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
    )

    assert list(rows.columns) == TRANSITION_ALIGNMENT_COLUMNS
    assert rows["Alignment_Method"].iloc[0] == "D1_INTERVAL_CONTAINMENT_MATCH"
    assert rows["D1_State_ID"].iloc[0] == "D1_STATE_000001"


def test_transition_builder_uses_date_fallback():
    d1 = d1_states().drop(columns=["D1_Period_Start", "D1_Period_End"])
    rows = build_h4_transition_alignment(
        h4_transitions().head(1),
        D1ContextIndex(d1, candle_map()),
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
    )

    assert rows["Alignment_Method"].iloc[0] == "D1_DATE_MATCH"


def test_transition_builder_marks_unmatched_without_fabricating_context():
    transition = h4_transitions().head(1).copy()
    transition["Transition_Time"] = "2026-08-01 12:00:00"
    transition["Transition_Date"] = "2026-08-01"

    rows = build_h4_transition_alignment(
        transition,
        D1ContextIndex(d1_states(), pd.DataFrame()),
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
    )

    assert rows["Alignment_Method"].iloc[0] == "NO_D1_SAME_TIME_MATCH"
    assert rows["D1_State_ID"].iloc[0] == ""
