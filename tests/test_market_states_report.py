from __future__ import annotations

from datetime import datetime, timedelta

from sqre.market_states.models import MarketState
from sqre.market_states.reports import MarketStatesReport


def state(index: int, market_state: str, confidence: float) -> MarketState:
    return MarketState(
        state_id=f"STATE_{index:06d}",
        structure_id=f"STR_{index:06d}",
        symbol="EURUSD",
        timeframe="M5",
        start_time=datetime(2026, 1, 1) + timedelta(minutes=index),
        end_time=datetime(2026, 1, 1) + timedelta(minutes=index + 5),
        direction="UP",
        market_state=market_state,
        state_confidence=confidence,
        classification_rule="test_rule",
        persistence_index=0.5,
        structural_complexity=0.5,
        structural_stability=0.5,
        structural_efficiency=0.5,
        event_density=0.5,
        structural_volatility=0.5,
        structural_symmetry=0.5,
        structural_confidence=0.7,
        lifecycle_stage="MATURITY",
    )


def test_market_states_report_is_generated_and_descriptive(tmp_path) -> None:
    report_path = tmp_path / "market_states_report.txt"
    MarketStatesReport().write(
        [
            state(1, "DIRECTIONAL_DRIFT", 0.7),
            state(2, "DIRECTIONAL_DRIFT", 0.8),
            state(3, "LOW_QUALITY_STRUCTURE", 0.6),
        ],
        report_path,
    )

    text = report_path.read_text(encoding="utf-8")

    assert report_path.exists()
    assert "- Directional Displacement: 0" in text
    assert "- Directional Drift: 2" in text
    assert "- Low Quality Structure: 1" in text
    assert "Most Common State: Directional Drift" in text
    assert "Average State Confidence:" in text
    for forbidden in [
        "Buy",
        "Sell",
        "Entry",
        "Exit",
        "Take Profit",
        "Stop Loss",
        "Reversal expected",
        "Continuation likely",
        "Prepare to buy",
    ]:
        assert forbidden not in text
