"""Transition metric calculations."""

from __future__ import annotations

from sqre.transition_engine.config import TransitionEngineConfig
from sqre.transition_engine.models import MarketStateInput, TransitionMetrics


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(value, maximum))


def calculate_transition_metrics(
    from_state: MarketStateInput,
    to_state: MarketStateInput,
    config: TransitionEngineConfig,
) -> TransitionMetrics:
    persistence_change = to_state.persistence_index - from_state.persistence_index
    complexity_change = to_state.structural_complexity - from_state.structural_complexity
    stability_change = to_state.structural_stability - from_state.structural_stability
    efficiency_change = to_state.structural_efficiency - from_state.structural_efficiency
    density_change = to_state.event_density - from_state.event_density
    volatility_change = to_state.structural_volatility - from_state.structural_volatility
    symmetry_change = to_state.structural_symmetry - from_state.structural_symmetry
    structural_confidence_change = to_state.structural_confidence - from_state.structural_confidence
    state_confidence_change = to_state.state_confidence - from_state.state_confidence
    price_displacement_change = to_state.price_displacement - from_state.price_displacement
    duration_change = to_state.duration_seconds - from_state.duration_seconds
    event_count_change = to_state.event_count - from_state.event_count
    leg_count_change = to_state.leg_count - from_state.leg_count

    persistence_abs_change = abs(persistence_change)
    complexity_abs_change = abs(complexity_change)
    stability_abs_change = abs(stability_change)
    efficiency_abs_change = abs(efficiency_change)
    density_abs_change = abs(density_change)
    volatility_abs_change = abs(volatility_change)
    symmetry_abs_change = abs(symmetry_change)
    structural_confidence_abs_change = abs(structural_confidence_change)
    state_confidence_abs_change = abs(state_confidence_change)

    transition_magnitude = _average(
        persistence_abs_change,
        complexity_abs_change,
        stability_abs_change,
        efficiency_abs_change,
        volatility_abs_change,
        state_confidence_abs_change,
    )
    transition_stability = clamp(1 - transition_magnitude)
    structural_quality_change = _average(
        stability_change,
        efficiency_change,
        structural_confidence_change,
        clamp_values=False,
    )

    return TransitionMetrics(
        persistence_change=persistence_change,
        complexity_change=complexity_change,
        stability_change=stability_change,
        efficiency_change=efficiency_change,
        density_change=density_change,
        volatility_change=volatility_change,
        symmetry_change=symmetry_change,
        structural_confidence_change=structural_confidence_change,
        state_confidence_change=state_confidence_change,
        price_displacement_change=price_displacement_change,
        duration_change=duration_change,
        event_count_change=event_count_change,
        leg_count_change=leg_count_change,
        persistence_abs_change=persistence_abs_change,
        complexity_abs_change=complexity_abs_change,
        stability_abs_change=stability_abs_change,
        efficiency_abs_change=efficiency_abs_change,
        density_abs_change=density_abs_change,
        volatility_abs_change=volatility_abs_change,
        symmetry_abs_change=symmetry_abs_change,
        structural_confidence_abs_change=structural_confidence_abs_change,
        state_confidence_abs_change=state_confidence_abs_change,
        transition_magnitude=transition_magnitude,
        transition_stability=transition_stability,
        structural_quality_change=structural_quality_change,
    )


def classify_confidence_transition(state_confidence_change: float, config: TransitionEngineConfig) -> str:
    if state_confidence_change >= config.confidence_change_threshold:
        return "CONFIDENCE_EXPANSION"
    if state_confidence_change <= -config.confidence_change_threshold:
        return "CONFIDENCE_DETERIORATION"
    return "CONFIDENCE_STABLE"


def classify_structural_transition(structural_quality_change: float, config: TransitionEngineConfig) -> str:
    if structural_quality_change >= config.structural_change_threshold:
        return "STRUCTURAL_IMPROVEMENT"
    if structural_quality_change <= -config.structural_change_threshold:
        return "STRUCTURAL_DETERIORATION"
    return "STRUCTURAL_STABLE"


def classify_magnitude(transition_magnitude: float, config: TransitionEngineConfig) -> str:
    if transition_magnitude >= config.high_magnitude_threshold:
        return "HIGH_MAGNITUDE"
    if transition_magnitude <= config.low_magnitude_threshold:
        return "LOW_MAGNITUDE"
    return "MODERATE_MAGNITUDE"


def _average(*values: float, clamp_values: bool = True) -> float:
    if not values:
        return 0.0
    value = sum(values) / len(values)
    return clamp(value) if clamp_values else value
