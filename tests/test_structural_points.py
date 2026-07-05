from __future__ import annotations

from datetime import datetime, timedelta

from sqre.market_structure.models import MarketEvent
from sqre.market_structure.structural_points import StructuralPointBuilder


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


def test_structural_points_prefer_swing_over_pivot_at_same_time() -> None:
    events = [
        event(1, "PIVOT_LOW", 1.1000, 0),
        event(2, "SWING_LOW", 1.0998, 0),
        event(3, "PIVOT_HIGH", 1.1010, 5),
    ]

    points = StructuralPointBuilder().build(events)

    assert len(points) == 2
    assert points[0].event_id == "EVT_000002"
    assert points[0].source_event_type == "SWING_LOW"
    assert points[0].point_type == "STRUCTURAL_LOW"


def test_structural_points_compress_consecutive_same_side_points() -> None:
    points = StructuralPointBuilder().build(
        [
            event(1, "PIVOT_LOW", 1.1000, 0),
            event(2, "PIVOT_LOW", 1.0990, 5),
            event(3, "PIVOT_HIGH", 1.1020, 10),
        ]
    )

    compressed = StructuralPointBuilder().compress(points)

    assert [point.point_type for point in compressed] == ["STRUCTURAL_LOW", "STRUCTURAL_HIGH"]
    assert compressed[0].price == 1.0990
    assert compressed[0].point_id == "SP_000001"
