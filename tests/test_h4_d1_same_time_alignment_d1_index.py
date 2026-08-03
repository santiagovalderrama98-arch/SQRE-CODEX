import pandas as pd

from sqre.h4_d1_same_time_alignment_table.d1_context_index import D1ContextIndex
from tests.h4_d1_same_time_alignment_test_utils import candle_map, d1_states


def test_d1_context_index_interval_containment_match():
    index = D1ContextIndex(d1_states(), candle_map())

    match = index.match("2026-07-01 12:00:00", "2026-07-01")

    assert match.alignment_method == "D1_INTERVAL_CONTAINMENT_MATCH"
    assert match.alignment_confidence_class == "HIGH_CONFIDENCE_SAME_TIME_ALIGNMENT"
    assert match.row["D1_State_ID"] == "D1_STATE_000001"


def test_d1_context_index_date_match_fallback():
    d1 = d1_states().drop(columns=["D1_Period_Start", "D1_Period_End"])
    index = D1ContextIndex(d1, candle_map())

    match = index.match("2026-07-01 12:00:00", "2026-07-01")

    assert match.alignment_method == "D1_DATE_MATCH"
    assert match.row["D1_State_ID"] == "D1_STATE_000001"


def test_d1_context_index_candle_map_date_fallback():
    d1 = d1_states()
    d1["D1_Period_Start"] = pd.NaT
    d1["D1_Period_End"] = pd.NaT
    index = D1ContextIndex(d1, candle_map())

    match = index.match("2026-07-03 04:00:00", "2026-07-03")

    assert match.alignment_method == "H4_D1_CANDLE_MAP_DATE_MATCH"
    assert match.row["D1_State_ID"] == "D1_STATE_000002"


def test_d1_context_index_returns_no_match_without_context():
    index = D1ContextIndex(pd.DataFrame(), pd.DataFrame())

    match = index.match("2026-07-01 12:00:00", "2026-07-01")

    assert match.alignment_method == "NO_D1_SAME_TIME_MATCH"
    assert match.row is None
