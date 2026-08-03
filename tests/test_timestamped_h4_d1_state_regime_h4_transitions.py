import pandas as pd

from sqre.timestamped_h4_d1_state_regime_generation.h4_transition_table_builder import (
    H4_TRANSITION_COLUMNS,
    build_h4_transition_table,
)


def _state_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "H4_State_ID": ["H4_STATE_000001", "H4_STATE_000002"],
            "Symbol": ["EURUSD", "EURUSD"],
            "Timeframe": ["H4", "H4"],
            "State_Start_Time": ["2026-07-01 00:00:00", "2026-07-03 00:00:00"],
            "State_End_Time": ["2026-07-02 20:00:00", "2026-07-04 20:00:00"],
            "Market_State": ["DIRECTIONAL_EXPANSION", "DIRECTIONAL_DISPLACEMENT"],
        }
    )


def test_h4_transition_table_builds_ordered_transition_rows():
    transitions = build_h4_transition_table(_state_rows())

    assert list(transitions.columns) == H4_TRANSITION_COLUMNS
    assert len(transitions) == 1
    assert transitions["Transition_Label"].iloc[0] == "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT"


def test_h4_transition_table_refuses_unordered_state_rows():
    states = _state_rows().iloc[::-1].reset_index(drop=True)

    transitions = build_h4_transition_table(states)

    assert transitions.empty


def test_h4_transition_table_refuses_missing_timestamps():
    states = _state_rows()
    states.loc[1, "State_Start_Time"] = None

    transitions = build_h4_transition_table(states)

    assert transitions.empty
