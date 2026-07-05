"""Market Structure grouping."""

from __future__ import annotations

from dataclasses import replace

from sqre.market_structure.config import MarketStructureConfig
from sqre.market_structure.fingerprints import FingerprintBuilder
from sqre.market_structure.metrics import StructuralMetricsCalculator
from sqre.market_structure.models import Leg, MarketEvent, MarketStructure, StructuralPoint


class StructureBuilder:
    """Build simple progressive structures from valid legs."""

    def __init__(self, config: MarketStructureConfig | None = None) -> None:
        self.config = config or MarketStructureConfig()
        self.metrics_calculator = StructuralMetricsCalculator(self.config)
        self.fingerprint_builder = FingerprintBuilder()

    def build(
        self,
        legs: list[Leg],
        points: list[StructuralPoint],
        events: list[MarketEvent],
    ) -> list[MarketStructure]:
        if len(legs) < 2:
            return []

        groups = self._group_legs(legs)
        structures: list[MarketStructure] = []
        for index, (group, is_terminated) in enumerate(groups, start=1):
            if len(group) < 2:
                continue

            structure_id = f"STR_{index:06d}"
            structure_legs = [replace(leg, structure_id=structure_id) for leg in group]
            structure_points = self._points_for_legs(structure_legs, points)
            structure_events = self._events_for_interval(events, structure_legs[0].start_time, structure_legs[-1].end_time)
            metrics = self.metrics_calculator.calculate(structure_events, structure_legs)
            fingerprint = self.fingerprint_builder.build(structure_id, metrics)

            structures.append(
                MarketStructure(
                    structure_id=structure_id,
                    symbol=structure_events[0].symbol if structure_events else "",
                    timeframe=structure_events[0].timeframe if structure_events else "",
                    start_time=structure_legs[0].start_time,
                    end_time=structure_legs[-1].end_time,
                    start_price=structure_legs[0].start_price,
                    end_price=structure_legs[-1].end_price,
                    direction=self._direction(structure_legs),
                    lifecycle_stage=self._lifecycle_stage(structure_legs, metrics.structural_confidence, is_terminated),
                    events=structure_events,
                    points=structure_points,
                    legs=structure_legs,
                    metrics=metrics,
                    fingerprint=fingerprint,
                )
            )

        return structures

    def _group_legs(self, legs: list[Leg]) -> list[tuple[list[Leg], bool]]:
        if self.config.max_structure_duration_seconds is None:
            return [(legs, False)]

        groups: list[tuple[list[Leg], bool]] = []
        current: list[Leg] = []
        for leg in legs:
            if not current:
                current.append(leg)
                continue

            duration = (leg.end_time - current[0].start_time).total_seconds()
            if duration > self.config.max_structure_duration_seconds:
                groups.append((current, True))
                current = [leg]
            else:
                current.append(leg)

        if current:
            groups.append((current, False))

        return groups

    def _points_for_legs(self, legs: list[Leg], points: list[StructuralPoint]) -> list[StructuralPoint]:
        point_ids = {legs[0].start_point_id}
        point_ids.update(leg.end_point_id for leg in legs)
        return [point for point in points if point.point_id in point_ids]

    def _events_for_interval(self, events: list[MarketEvent], start, end) -> list[MarketEvent]:
        return [event for event in events if start <= event.date <= end]

    def _direction(self, legs: list[Leg]) -> str:
        if not legs:
            return "NEUTRAL"

        net_displacement_pips = abs(legs[-1].end_price - legs[0].start_price) / self.config.pip_size
        if net_displacement_pips < self.config.neutral_threshold_pips:
            return "NEUTRAL"
        if legs[-1].end_price > legs[0].start_price:
            return "UP"
        if legs[-1].end_price < legs[0].start_price:
            return "DOWN"
        return "NEUTRAL"

    def _lifecycle_stage(self, legs: list[Leg], confidence: float, is_terminated: bool = False) -> str:
        if is_terminated:
            return "TERMINATED"
        if len(legs) == 2:
            return "FORMATION"
        if len(legs) == 3:
            return "DEVELOPMENT"
        if len(legs) >= 4 and confidence >= self.config.min_structure_confidence:
            return "MATURITY"
        return "DEVELOPMENT"
