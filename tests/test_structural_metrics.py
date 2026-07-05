from __future__ import annotations

from datetime import datetime, timedelta

from sqre.market_structure.metrics import StructuralMetricsCalculator
from sqre.market_structure.models import Leg, MarketEvent


def event(index: int, event_type: str, minutes: int) -> MarketEvent:
    return MarketEvent(
        event_id=f"EVT_{index:06d}",
        date=datetime(2026, 1, 1) + timedelta(minutes=minutes),
        event_type=event_type,
        symbol="EURUSD",
        timeframe="M5",
        price=1.1000,
        value=1.1000,
    )


def leg(index: int, direction: str, distance: float, minutes: int) -> Leg:
    start = datetime(2026, 1, 1) + timedelta(minutes=minutes)
    end = start + timedelta(minutes=5)
    return Leg(
        leg_id=f"LEG_{index:06d}",
        structure_id="STR_000001",
        start_point_id=f"SP_{index:06d}",
        end_point_id=f"SP_{index + 1:06d}",
        start_time=start,
        end_time=end,
        start_price=1.1000,
        end_price=1.1000 + (distance * 0.0001),
        direction=direction,
        duration_seconds=300,
        distance_pips=distance,
        event_count=2,
        expansion_count=1 if direction == "UP" else 0,
        contraction_count=1 if direction == "DOWN" else 0,
        large_candle_count=0,
        small_candle_count=0,
        internal_pivot_count=1,
        confidence=0.8,
    )


def test_structural_metrics_are_bounded_and_descriptive() -> None:
    metrics = StructuralMetricsCalculator().calculate(
        [
            event(1, "PIVOT_LOW", 0),
            event(2, "RANGE_EXPANSION", 2),
            event(3, "PIVOT_HIGH", 5),
            event(4, "RANGE_CONTRACTION", 8),
        ],
        [leg(1, "UP", 10, 0), leg(2, "DOWN", 8, 5)],
    )

    assert metrics.event_count == 4
    assert metrics.leg_count == 2
    assert metrics.gross_distance_pips == 18
    assert 0 <= metrics.persistence_index <= 1
    assert 0 <= metrics.structural_complexity <= 1
    assert 0 <= metrics.structural_confidence <= 1
