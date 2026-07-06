from __future__ import annotations

from datetime import datetime, timedelta

from sqre.transition_engine.config import TransitionEngineConfig
from sqre.transition_engine.metrics import (
    calculate_transition_metrics,
    clamp,
    classify_confidence_transition,
    classify_magnitude,
    classify_structural_transition,
)
from sqre.transition_engine.models import MarketStateInput


def state(**overrides) -> MarketStateInput:
    data = {
        "state_id": "STATE_000001",
        "structure_id": "STR_000001",
        "symbol": "EURUSD",
        "timeframe": "M5",
        "start_time": datetime(2026, 1, 1),
        "end_time": datetime(2026, 1, 1) + timedelta(minutes=5),
        "direction": "UP",
        "market_state": "DIRECTIONAL_EXPANSION",
        "state_confidence": 0.5,
        "classification_rule": "rule",
        "persistence_index": 0.2,
        "structural_complexity": 0.3,
        "structural_stability": 0.4,
        "structural_efficiency": 0.5,
        "event_density": 0.6,
        "structural_volatility": 0.2,
        "structural_symmetry": 0.7,
        "structural_confidence": 0.5,
        "duration_seconds": 300,
        "price_displacement": 0.001,
        "event_count": 4,
        "leg_count": 2,
    }
    data.update(overrides)
    return MarketStateInput(**data)


def test_transition_metric_deltas_abs_changes_magnitude_and_stability() -> None:
    from_state = state()
    to_state = state(
        state_id="STATE_000002",
        persistence_index=0.4,
        structural_complexity=0.1,
        structural_stability=0.8,
        structural_efficiency=0.6,
        event_density=0.2,
        structural_volatility=0.7,
        structural_symmetry=0.6,
        structural_confidence=0.8,
        state_confidence=0.9,
        duration_seconds=600,
        price_displacement=-0.001,
        event_count=7,
        leg_count=3,
    )

    metrics = calculate_transition_metrics(from_state, to_state, TransitionEngineConfig())

    assert round(metrics.persistence_change, 4) == 0.2
    assert round(metrics.complexity_change, 4) == -0.2
    assert round(metrics.state_confidence_change, 4) == 0.4
    assert round(metrics.price_displacement_change, 4) == -0.002
    assert metrics.duration_change == 300
    assert metrics.event_count_change == 3
    assert metrics.leg_count_change == 1
    assert round(metrics.complexity_abs_change, 4) == 0.2
    expected_magnitude = (0.2 + 0.2 + 0.4 + 0.1 + 0.5 + 0.4) / 6
    assert round(metrics.transition_magnitude, 4) == round(expected_magnitude, 4)
    assert round(metrics.transition_stability, 4) == round(1 - expected_magnitude, 4)
    assert round(metrics.structural_quality_change, 4) == round((0.4 + 0.1 + 0.3) / 3, 4)


def test_transition_classification_helpers_and_clamp() -> None:
    config = TransitionEngineConfig()

    assert clamp(-1) == 0.0
    assert clamp(2) == 1.0
    assert classify_confidence_transition(0.2, config) == "CONFIDENCE_EXPANSION"
    assert classify_confidence_transition(-0.2, config) == "CONFIDENCE_DETERIORATION"
    assert classify_confidence_transition(0.05, config) == "CONFIDENCE_STABLE"
    assert classify_structural_transition(0.2, config) == "STRUCTURAL_IMPROVEMENT"
    assert classify_structural_transition(-0.2, config) == "STRUCTURAL_DETERIORATION"
    assert classify_structural_transition(0.02, config) == "STRUCTURAL_STABLE"
    assert classify_magnitude(0.5, config) == "HIGH_MAGNITUDE"
    assert classify_magnitude(0.1, config) == "LOW_MAGNITUDE"
    assert classify_magnitude(0.3, config) == "MODERATE_MAGNITUDE"
