"""Structural metrics for SQRE Market Structure v1.0."""

from __future__ import annotations

from statistics import mean, pstdev

from sqre.market_structure.config import MarketStructureConfig
from sqre.market_structure.models import Leg, MarketEvent, StructuralMetrics


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(value, maximum))


class StructuralMetricsCalculator:
    """Calculate deterministic descriptive structural metrics."""

    _SMALL_NUMBER = 1e-9

    def __init__(self, config: MarketStructureConfig | None = None) -> None:
        self.config = config or MarketStructureConfig()

    def calculate(self, events: list[MarketEvent], legs: list[Leg]) -> StructuralMetrics:
        event_count = len(events)
        pivot_count = sum(1 for event in events if event.event_type.startswith("PIVOT"))
        swing_count = sum(1 for event in events if event.event_type.startswith("SWING"))
        large_candle_count = self._count(events, "LARGE_CANDLE")
        small_candle_count = self._count(events, "SMALL_CANDLE")
        range_expansion_count = self._count(events, "RANGE_EXPANSION")
        range_contraction_count = self._count(events, "RANGE_CONTRACTION")

        leg_count = len(legs)
        up_leg_count = sum(1 for leg in legs if leg.direction == "UP")
        down_leg_count = sum(1 for leg in legs if leg.direction == "DOWN")
        direction_changes = self._direction_changes(legs)
        distances = [abs(leg.distance_pips) for leg in legs]
        gross_distance_pips = sum(distances)
        net_displacement_pips = self._net_displacement(legs)
        average_leg_distance_pips = gross_distance_pips / max(leg_count, 1)
        max_leg_distance_pips = max(distances) if distances else 0.0
        min_leg_distance_pips = min(distances) if distances else 0.0

        persistence_index = self._persistence_index(
            up_leg_count,
            down_leg_count,
            leg_count,
            net_displacement_pips,
            gross_distance_pips,
            range_expansion_count,
            range_contraction_count,
        )
        structural_complexity = self._structural_complexity(
            leg_count,
            event_count,
            direction_changes,
            pivot_count,
        )
        structural_stability = self._structural_stability(
            event_count,
            leg_count,
            small_candle_count,
            range_contraction_count,
            direction_changes,
            legs,
        )
        structural_efficiency = clamp(
            (net_displacement_pips / max(event_count, 1)) / self.config.efficiency_reference_pips_per_event
        )
        event_density = self._event_density(event_count, legs)
        structural_volatility = clamp(average_leg_distance_pips / self.config.volatility_reference_pips)
        structural_symmetry = self._structural_symmetry(distances)
        structural_confidence = self._structural_confidence(leg_count, persistence_index, structural_stability)

        return StructuralMetrics(
            event_count=event_count,
            pivot_count=pivot_count,
            swing_count=swing_count,
            large_candle_count=large_candle_count,
            small_candle_count=small_candle_count,
            range_expansion_count=range_expansion_count,
            range_contraction_count=range_contraction_count,
            leg_count=leg_count,
            up_leg_count=up_leg_count,
            down_leg_count=down_leg_count,
            direction_changes=direction_changes,
            gross_distance_pips=gross_distance_pips,
            net_displacement_pips=net_displacement_pips,
            average_leg_distance_pips=average_leg_distance_pips,
            max_leg_distance_pips=max_leg_distance_pips,
            min_leg_distance_pips=min_leg_distance_pips,
            persistence_index=persistence_index,
            structural_complexity=structural_complexity,
            structural_stability=structural_stability,
            structural_efficiency=structural_efficiency,
            event_density=event_density,
            structural_volatility=structural_volatility,
            structural_symmetry=structural_symmetry,
            structural_confidence=structural_confidence,
        )

    def _count(self, events: list[MarketEvent], event_type: str) -> int:
        return sum(1 for event in events if event.event_type == event_type)

    def _direction_changes(self, legs: list[Leg]) -> int:
        return sum(1 for current, previous in zip(legs[1:], legs[:-1]) if current.direction != previous.direction)

    def _net_displacement(self, legs: list[Leg]) -> float:
        if not legs:
            return 0.0
        return abs(legs[-1].end_price - legs[0].start_price) / self.config.pip_size

    def _persistence_index(
        self,
        up_leg_count: int,
        down_leg_count: int,
        leg_count: int,
        net_displacement_pips: float,
        gross_distance_pips: float,
        range_expansion_count: int,
        range_contraction_count: int,
    ) -> float:
        directional_consistency = max(up_leg_count, down_leg_count) / max(leg_count, 1)
        displacement_efficiency = net_displacement_pips / max(gross_distance_pips, self._SMALL_NUMBER)
        if range_expansion_count + range_contraction_count == 0:
            expansion_balance = 0.50
        else:
            expansion_balance = range_expansion_count / (range_expansion_count + range_contraction_count)
        return clamp((0.40 * directional_consistency) + (0.35 * displacement_efficiency) + (0.25 * expansion_balance))

    def _structural_complexity(
        self,
        leg_count: int,
        event_count: int,
        direction_changes: int,
        pivot_count: int,
    ) -> float:
        leg_factor = min(leg_count / 10, 1.0)
        event_factor = min(event_count / 50, 1.0)
        direction_change_factor = direction_changes / max(leg_count - 1, 1)
        pivot_density_factor = min(pivot_count / max(event_count, 1), 1.0)
        return clamp(
            (0.30 * leg_factor)
            + (0.30 * event_factor)
            + (0.25 * direction_change_factor)
            + (0.15 * pivot_density_factor)
        )

    def _structural_stability(
        self,
        event_count: int,
        leg_count: int,
        small_candle_count: int,
        range_contraction_count: int,
        direction_changes: int,
        legs: list[Leg],
    ) -> float:
        noise_ratio = (small_candle_count + range_contraction_count) / max(event_count, 1)
        direction_change_ratio = direction_changes / max(leg_count - 1, 1)
        short_leg_count = sum(1 for leg in legs if leg.distance_pips < self.config.min_leg_pips * 1.5)
        short_leg_ratio = short_leg_count / max(leg_count, 1)
        return clamp(1 - ((0.40 * noise_ratio) + (0.35 * direction_change_ratio) + (0.25 * short_leg_ratio)))

    def _event_density(self, event_count: int, legs: list[Leg]) -> float:
        if not legs:
            return 0.0
        duration_seconds = max((legs[-1].end_time - legs[0].start_time).total_seconds(), 0.0)
        events_per_hour = event_count / max(duration_seconds / 3600, 1)
        return clamp(events_per_hour / self.config.density_reference_events_per_hour)

    def _structural_symmetry(self, distances: list[float]) -> float:
        if not distances:
            return 0.0
        average_leg_distance = mean(distances)
        leg_distance_std = pstdev(distances) if len(distances) > 1 else 0.0
        coefficient_of_variation = leg_distance_std / max(average_leg_distance, self._SMALL_NUMBER)
        return clamp(1 / (1 + coefficient_of_variation))

    def _structural_confidence(self, leg_count: int, persistence_index: float, structural_stability: float) -> float:
        minimum_leg_score = min(leg_count / 4, 1.0)
        traceability_score = 1.0
        return clamp(
            (0.30 * minimum_leg_score)
            + (0.30 * persistence_index)
            + (0.25 * structural_stability)
            + (0.15 * traceability_score)
        )
