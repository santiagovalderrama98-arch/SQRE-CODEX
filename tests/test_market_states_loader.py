from __future__ import annotations

import pandas as pd
import pytest

from sqre.market_states.loader import MarketStatesLoader


def structures_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Structure_ID": ["STR_000002", "STR_000001"],
            "Symbol": ["EURUSD", "EURUSD"],
            "Timeframe": ["M5", "M5"],
            "Start_Time": ["2026-01-01 00:05:00", "2026-01-01 00:00:00"],
            "End_Time": ["2026-01-01 00:10:00", "2026-01-01 00:05:00"],
            "Direction": ["down", "UP"],
            "Lifecycle_Stage": ["maturity", "formation"],
            "Persistence_Index": [0.4, 0.6],
            "Structural_Complexity": [0.5, 0.6],
            "Structural_Stability": [0.7, 0.8],
            "Structural_Efficiency": [0.3, 0.7],
            "Event_Density": [0.4, 0.5],
            "Structural_Volatility": [0.2, 0.3],
            "Structural_Symmetry": [0.8, 0.9],
            "Structural_Confidence": [0.7, 0.8],
            "Duration_Seconds": [300, 300],
            "Price_Displacement": [-0.0002, 0.0004],
            "Event_Count": [4, 5],
            "Leg_Count": [2, 3],
            "Extra_Column": ["ok", "ok"],
        }
    )


def test_market_states_loader_loads_sorts_and_tolerates_extra_columns(tmp_path) -> None:
    path = tmp_path / "structures.csv"
    structures_frame().to_csv(path, index=False)

    structures = MarketStatesLoader().load(path)

    assert [structure.structure_id for structure in structures] == ["STR_000001", "STR_000002"]
    assert structures[0].start_time < structures[1].start_time
    assert structures[0].direction == "UP"
    assert structures[0].lifecycle_stage == "FORMATION"
    assert structures[0].duration_seconds == 300
    assert structures[0].event_count == 5


def test_market_states_loader_rejects_missing_required_columns(tmp_path) -> None:
    path = tmp_path / "structures.csv"
    data = structures_frame().drop(columns=["Structural_Confidence"])
    data.to_csv(path, index=False)

    with pytest.raises(ValueError, match="Missing required structure columns"):
        MarketStatesLoader().load(path)
