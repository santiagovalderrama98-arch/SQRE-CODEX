"""Leg construction for Market Structure."""

from __future__ import annotations

from sqre.market_structure.config import MarketStructureConfig
from sqre.market_structure.models import Leg, MarketEvent, StructuralPoint


class LegBuilder:
    """Create valid legs between alternating structural points."""

    def __init__(self, config: MarketStructureConfig | None = None) -> None:
        self.config = config or MarketStructureConfig()

    def build(self, points: list[StructuralPoint], events: list[MarketEvent], *, structure_id: str = "") -> list[Leg]:
        legs: list[Leg] = []
        for start, end in zip(points, points[1:]):
            leg = self._build_leg(start, end, events, structure_id=structure_id, index=len(legs) + 1)
            if leg is not None:
                legs.append(leg)
        return legs

    def _build_leg(
        self,
        start: StructuralPoint,
        end: StructuralPoint,
        events: list[MarketEvent],
        *,
        structure_id: str,
        index: int,
    ) -> Leg | None:
        if start.point_type == end.point_type:
            return None

        direction = self._direction(start, end)
        distance_pips = abs(end.price - start.price) / self.config.pip_size
        if distance_pips < self.config.min_leg_pips:
            return None

        internal_events = [event for event in events if start.time <= event.date <= end.time]
        duration_seconds = max((end.time - start.time).total_seconds(), 0.0)
        confidence = min(distance_pips / (self.config.min_leg_pips * 2), 1.0)

        return Leg(
            leg_id=f"LEG_{index:06d}",
            structure_id=structure_id,
            start_point_id=start.point_id,
            end_point_id=end.point_id,
            start_time=start.time,
            end_time=end.time,
            start_price=start.price,
            end_price=end.price,
            direction=direction,
            duration_seconds=duration_seconds,
            distance_pips=distance_pips,
            event_count=len(internal_events),
            expansion_count=self._count(internal_events, "RANGE_EXPANSION"),
            contraction_count=self._count(internal_events, "RANGE_CONTRACTION"),
            large_candle_count=self._count(internal_events, "LARGE_CANDLE"),
            small_candle_count=self._count(internal_events, "SMALL_CANDLE"),
            internal_pivot_count=sum(1 for event in internal_events if event.event_type.startswith("PIVOT")),
            confidence=confidence,
        )

    def _direction(self, start: StructuralPoint, end: StructuralPoint) -> str:
        if start.point_type == "STRUCTURAL_LOW" and end.point_type == "STRUCTURAL_HIGH":
            return "UP"
        if start.point_type == "STRUCTURAL_HIGH" and end.point_type == "STRUCTURAL_LOW":
            return "DOWN"
        return "NEUTRAL"

    def _count(self, events: list[MarketEvent], event_type: str) -> int:
        return sum(1 for event in events if event.event_type == event_type)
