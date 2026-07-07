from __future__ import annotations

import pandas as pd
import pytest

from sqre.price_outcome_research.loader import (
    load_ohlc,
    load_price_outcome_states,
    load_price_outcome_transitions,
)
from tests.price_outcome_test_utils import STATE_ROWS, write_price_outcome_inputs


def test_price_outcome_loader_reads_sorts_and_tolerates_extra_columns(tmp_path) -> None:
    states_path, transitions_path, ohlc_path = write_price_outcome_inputs(tmp_path)

    states = load_price_outcome_states(states_path)
    transitions = load_price_outcome_transitions(transitions_path)
    candles = load_ohlc(ohlc_path)

    assert [state.state_id for state in states] == ["S1", "S2", "S3", "S4"]
    assert [transition.transition_id for transition in transitions] == ["T1", "T2", "T3"]
    assert candles[0].date.isoformat() == "2026-01-01T00:00:00"
    assert states[0].duration_seconds == 3600
    assert states[0].price_displacement == 0.001


def test_price_outcome_loader_applies_optional_defaults(tmp_path) -> None:
    states_path = tmp_path / "states.csv"
    frame = pd.DataFrame(STATE_ROWS).drop(columns=["Duration_Seconds", "Price_Displacement"])
    frame.to_csv(states_path, index=False)

    states = load_price_outcome_states(states_path)

    assert states[0].duration_seconds == 0.0
    assert states[0].price_displacement == 0.0


def test_price_outcome_loader_fails_for_missing_required_column(tmp_path) -> None:
    states_path = tmp_path / "bad_states.csv"
    pd.DataFrame({"State_ID": ["S1"]}).to_csv(states_path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_price_outcome_states(states_path)
