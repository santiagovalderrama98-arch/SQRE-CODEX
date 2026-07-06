from __future__ import annotations

import pandas as pd

from sqre.market_states.market_states_pipeline import MarketStatesPipeline


def test_market_states_pipeline_writes_outputs(tmp_path) -> None:
    structures_path = tmp_path / "structures.csv"
    output_path = tmp_path / "market_states.csv"
    report_path = tmp_path / "market_states_report.txt"
    pd.DataFrame(
        {
            "Structure_ID": ["STR_000001", "STR_000002", "STR_000003", "STR_000004"],
            "Symbol": ["EURUSD", "EURUSD", "EURUSD", "EURUSD"],
            "Timeframe": ["M5", "M5", "M5", "M5"],
            "Start_Time": pd.date_range("2026-01-01", periods=4, freq="5min"),
            "End_Time": pd.date_range("2026-01-01 00:05:00", periods=4, freq="5min"),
            "Direction": ["UP", "DOWN", "NEUTRAL", "UP"],
            "Lifecycle_Stage": ["MATURITY", "FORMATION", "DEVELOPMENT", "DEVELOPMENT"],
            "Persistence_Index": [0.6, 0.4, 0.2, 0.2],
            "Structural_Complexity": [0.4, 0.5, 0.4, 0.4],
            "Structural_Stability": [0.8, 0.7, 0.7, 0.7],
            "Structural_Efficiency": [0.7, 0.4, 0.2, 0.7],
            "Event_Density": [0.5, 0.4, 0.3, 0.4],
            "Structural_Volatility": [0.3, 0.4, 0.2, 0.3],
            "Structural_Symmetry": [0.8, 0.8, 0.8, 0.7],
            "Structural_Confidence": [0.8, 0.75, 0.7, 0.6],
            "Duration_Seconds": [300, 300, 300, 300],
            "Price_Displacement": [0.001, -0.0004, 0.0, 0.0008],
            "Event_Count": [8, 7, 6, 5],
            "Leg_Count": [4, 3, 2, 3],
        }
    ).to_csv(structures_path, index=False)

    result = MarketStatesPipeline().run(
        structures_path=structures_path,
        output_path=output_path,
        report_path=report_path,
    )

    assert result.success
    assert result.structures_processed == 4
    assert result.states_generated == 4
    assert output_path.exists()
    assert report_path.exists()

    output = pd.read_csv(output_path)
    assert len(output) == 4
    assert {
        "State_ID",
        "Structure_ID",
        "Market_State",
        "State_Confidence",
        "Classification_Rule",
    }.issubset(output.columns)
    assert output["Classification_Rule"].notna().all()
    assert output["State_Confidence"].between(0, 1).all()
    assert "DIRECTIONAL_DISPLACEMENT" in set(output["Market_State"])
    assert "SQRE Market States Report" in report_path.read_text(encoding="utf-8")


def test_market_states_pipeline_uses_deterministic_state_order_for_ties() -> None:
    pipeline = MarketStatesPipeline()
    states = [
        type("State", (), {"market_state": "NEUTRAL_COMPRESSION"})(),
        type("State", (), {"market_state": "DIRECTIONAL_EXPANSION"})(),
    ]

    assert pipeline._most_common_state(states) == "DIRECTIONAL_EXPANSION"
