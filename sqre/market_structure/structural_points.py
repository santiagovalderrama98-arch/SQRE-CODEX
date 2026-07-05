"""Structural point construction and compression."""

from __future__ import annotations

from sqre.market_structure.models import MarketEvent, StructuralPoint


class StructuralPointBuilder:
    """Build structural highs/lows from primary structural events."""

    _POINT_MAP = {
        "PIVOT_HIGH": "STRUCTURAL_HIGH",
        "SWING_HIGH": "STRUCTURAL_HIGH",
        "PIVOT_LOW": "STRUCTURAL_LOW",
        "SWING_LOW": "STRUCTURAL_LOW",
    }
    _PRIORITY = {
        "SWING_HIGH": 3,
        "SWING_LOW": 3,
        "PIVOT_HIGH": 2,
        "PIVOT_LOW": 2,
    }

    def build(self, events: list[MarketEvent]) -> list[StructuralPoint]:
        candidates = [event for event in events if event.event_type in self._POINT_MAP]
        grouped: dict[tuple[object, str], MarketEvent] = {}
        for event in candidates:
            point_type = self._POINT_MAP[event.event_type]
            key = (event.date, point_type)
            current = grouped.get(key)
            if current is None or self._priority(event) > self._priority(current):
                grouped[key] = event

        points: list[StructuralPoint] = []
        for index, event in enumerate(sorted(grouped.values(), key=lambda item: (item.date, item.event_id)), start=1):
            point_type = self._POINT_MAP[event.event_type]
            points.append(
                StructuralPoint(
                    point_id=f"SP_{index:06d}",
                    event_id=event.event_id,
                    time=event.date,
                    point_type=point_type,
                    price=event.price,
                    source_event_type=event.event_type,
                    priority=self._priority(event),
                )
            )
        return points

    def compress(self, points: list[StructuralPoint]) -> list[StructuralPoint]:
        if not points:
            return []

        compressed: list[StructuralPoint] = []
        run: list[StructuralPoint] = [points[0]]
        for point in points[1:]:
            if point.point_type == run[-1].point_type:
                run.append(point)
            else:
                compressed.append(self._select_from_run(run))
                run = [point]
        compressed.append(self._select_from_run(run))
        return self._renumber(compressed)

    def _priority(self, event: MarketEvent) -> int:
        return self._PRIORITY.get(event.event_type, 1)

    def _select_from_run(self, run: list[StructuralPoint]) -> StructuralPoint:
        if run[0].point_type == "STRUCTURAL_HIGH":
            return max(run, key=lambda point: (point.price, point.priority))
        return min(run, key=lambda point: (point.price, -point.priority))

    def _renumber(self, points: list[StructuralPoint]) -> list[StructuralPoint]:
        return [
            StructuralPoint(
                point_id=f"SP_{index:06d}",
                event_id=point.event_id,
                time=point.time,
                point_type=point.point_type,
                price=point.price,
                source_event_type=point.source_event_type,
                priority=point.priority,
            )
            for index, point in enumerate(points, start=1)
        ]
