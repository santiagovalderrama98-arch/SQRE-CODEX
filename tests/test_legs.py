from __future__ import annotations

from datetime import datetime, timedelta

from sqre.market_structure.config import MarketStructureConfig
from sqre.market_structure.legs import LegBuilder
from sqre.market_structure.models import MarketEvent, StructuralPoint


def point(index: int, point_type: str, price: float, minutes: int) -> StructuralPoint:
    source = "PIVOT_LOW" if point_type == "STRUCTURAL_LOW" else "PIVOT_HIGH"
    return StructuralPoint(
        point_id=f"SP_{index:06d}",
        event_id=f"EVT_{index:06d}",
        time=datetime(2026, 1, 1) + timedelta(minutes=minutes),
        point_type=point_type,
        price=price,
        source_event_type=source,
        priority=2,
    )


def event(index: int, event_type: str, price: float, minutes: int) -> MarketEvent:
    return MarketEvent(
        event_id=f"EVT_{index:06d}",
        date=datetime(2026, 1, 1) + timedelta(minutes=minutes),
        event_type=event_type,
        symbol="EURUSD",
        timeframe="M5",
        price=price,
        value=price,
    )


def test_leg_builder_creates_alternating_directional_legs() -> None:
    points = [
        point(1, "STRUCTURAL_LOW", 1.1000, 0),
        point(2, "STRUCTURAL_HIGH", 1.1010, 5),
        point(3, "STRUCTURAL_LOW", 1.1002, 10),
    ]
    events = [
        event(1, "PIVOT_LOW", 1.1000, 0),
        event(2, "RANGE_EXPANSION", 1.1005, 3),
        event(3, "PIVOT_HIGH", 1.1010, 5),
        event(4, "SMALL_CANDLE", 1.1006, 8),
    ]

    legs = LegBuilder().build(points, events)

    assert [leg.direction for leg in legs] == ["UP", "DOWN"]
    assert round(legs[0].distance_pips, 1) == 10.0
    assert legs[0].expansion_count == 1
    assert legs[1].small_candle_count == 1


def test_leg_builder_filters_small_legs() -> None:
    points = [
        point(1, "STRUCTURAL_LOW", 1.1000, 0),
        point(2, "STRUCTURAL_HIGH", 1.1001, 5),
    ]

    legs = LegBuilder(MarketStructureConfig(min_leg_pips=3.0)).build(points, [])

    assert legs == []
