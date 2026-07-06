from __future__ import annotations

import pandas as pd
import pytest

from sqre.transition_engine.loader import load_market_states


def market_states_frame(**overrides) -> pd.DataFrame:
    data = {
        "State_ID": ["STATE_000002", "STATE_000001"],
        "Structure_ID": ["STR_000002", "STR_000001"],
        "Symbol": ["EURUSD", "EURUSD"],
        "Timeframe": ["M5", "M5"],
        "Start_Time": ["2026-01-01 00:05:00", "2026-01-01 00:00:00"],
        "End_Time": ["2026-01-01 00:10:00", "2026-01-01 00:05:00"],
        "Direction": ["DOWN", "UP"],
        "Market_State": ["DIRECTIONAL_DRIFT", "DIRECTIONAL_EXPANSION"],
        "State_Confidence": [0.6, 0.8],
        "Classification_Rule": ["directional_drift_rule", "directional_expansion_rule"],
        "Persistence_Index": [0.3, 0.7],
        "Structural_Complexity": [0.4, 0.5],
        "Structural_Stability": [0.6, 0.7],
        "Structural_Efficiency": [0.5, 0.8],
        "Event_Density": [0.4, 0.5],
        "Structural_Volatility": [0.3, 0.2],
        "Structural_Symmetry": [0.7, 0.8],
        "Structural_Confidence": [0.65, 0.85],
    }
    data.update(overrides)
    return pd.DataFrame(data)


def test_load_market_states_validates_sorts_dates_and_defaults(tmp_path) -> None:
    path = tmp_path / "market_states.csv"
    frame = market_states_frame(Extra_Column=["ignored", "ignored"])
    frame.to_csv(path, index=False)

    states = load_market_states(path)

    assert [state.state_id for state in states] == ["STATE_000001", "STATE_000002"]
    assert states[0].start_time.year == 2026
    assert states[0].lifecycle_stage == ""
    assert states[0].duration_seconds == 0.0
    assert states[0].price_displacement == 0.0
    assert states[0].event_count == 0
    assert states[0].leg_count == 0


def test_load_market_states_uses_optional_values_when_present(tmp_path) -> None:
    path = tmp_path / "market_states.csv"
    market_states_frame(
        Lifecycle_Stage=["MATURITY", "FORMATION"],
        Duration_Seconds=[300, 600],
        Price_Displacement=[0.001, -0.002],
        Event_Count=[5, 7],
        Leg_Count=[2, 3],
    ).to_csv(path, index=False)

    states = load_market_states(path)

    assert states[0].lifecycle_stage == "FORMATION"
    assert states[0].duration_seconds == 600
    assert states[0].price_displacement == -0.002
    assert states[0].event_count == 7
    assert states[0].leg_count == 3


def test_load_market_states_fails_clearly_when_required_column_is_missing(tmp_path) -> None:
    path = tmp_path / "market_states.csv"
    market_states_frame().drop(columns=["Market_State"]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Market_State"):
        load_market_states(path)
