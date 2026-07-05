from __future__ import annotations

from datetime import datetime, timedelta

from sqre.market_structure.config import MarketStructureConfig
from sqre.market_structure.legs import LegBuilder
from sqre.market_structure.models import MarketEvent, StructuralPoint
from sqre.market_structure.structures import StructureBuilder


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


def sample_points() -> list[StructuralPoint]:
    return [
        point(1, "STRUCTURAL_LOW", 1.1000, 0),
        point(2, "STRUCTURAL_HIGH", 1.1010, 5),
        point(3, "STRUCTURAL_LOW", 1.1002, 10),
        point(4, "STRUCTURAL_HIGH", 1.1020, 15),
        point(5, "STRUCTURAL_LOW", 1.1010, 20),
    ]


def sample_events() -> list[MarketEvent]:
    return [
        event(1, "PIVOT_LOW", 1.1000, 0),
        event(2, "PIVOT_HIGH", 1.1010, 5),
        event(3, "RANGE_EXPANSION", 1.1008, 7),
        event(4, "PIVOT_LOW", 1.1002, 10),
        event(5, "PIVOT_HIGH", 1.1020, 15),
        event(6, "PIVOT_LOW", 1.1010, 20),
    ]


def test_structure_builder_creates_mature_traceable_structure() -> None:
    points = sample_points()
    events = sample_events()
    legs = LegBuilder().build(points, events)

    structures = StructureBuilder().build(legs, points, events)

    assert len(structures) == 1
    assert structures[0].structure_id == "STR_000001"
    assert structures[0].lifecycle_stage == "MATURITY"
    assert structures[0].metrics is not None
    assert structures[0].fingerprint is not None
    assert all(leg.structure_id == "STR_000001" for leg in structures[0].legs)


def test_structure_builder_marks_duration_split_groups_as_terminated() -> None:
    points = sample_points()
    events = sample_events()
    legs = LegBuilder().build(points, events)
    config = MarketStructureConfig(max_structure_duration_seconds=700)

    structures = StructureBuilder(config).build(legs, points, events)

    assert structures
    assert structures[0].lifecycle_stage == "TERMINATED"
