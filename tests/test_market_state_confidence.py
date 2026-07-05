from __future__ import annotations

from datetime import datetime, timedelta

from sqre.market_states.confidence import StateConfidenceCalculator, clamp
from sqre.market_states.models import StateClassificationResult, StructuralInput


def structure(**overrides) -> StructuralInput:
    data = {
        "structure_id": "STR_000001",
        "symbol": "EURUSD",
        "timeframe": "M5",
        "start_time": datetime(2026, 1, 1),
        "end_time": datetime(2026, 1, 1) + timedelta(minutes=5),
        "direction": "UP",
        "lifecycle_stage": "MATURITY",
        "persistence_index": 0.6,
        "structural_complexity": 0.7,
        "structural_stability": 0.8,
        "structural_efficiency": 0.4,
        "event_density": 0.5,
        "structural_volatility": 0.8,
        "structural_symmetry": 0.8,
        "structural_confidence": 0.7,
    }
    data.update(overrides)
    return StructuralInput(**data)


def confidence(market_state: str, input_structure: StructuralInput | None = None) -> float:
    input_structure = input_structure or structure()
    return StateConfidenceCalculator().calculate(input_structure, StateClassificationResult(market_state, "rule"))


def test_clamp_bounds_values() -> None:
    assert clamp(-1) == 0.0
    assert clamp(2) == 1.0
    assert clamp(0.5) == 0.5


def test_confidence_values_are_normalized_for_all_states() -> None:
    for state in [
        "LOW_QUALITY_STRUCTURE",
        "DIRECTIONAL_EXPANSION",
        "DIRECTIONAL_DRIFT",
        "NEUTRAL_COMPRESSION",
        "COMPLEX_CONSOLIDATION",
        "VOLATILE_ROTATION",
        "UNCLASSIFIED",
    ]:
        value = confidence(state)
        assert 0 <= value <= 1


def test_low_quality_structure_confidence() -> None:
    assert confidence("LOW_QUALITY_STRUCTURE", structure(structural_confidence=0.4)) == 0.6


def test_directional_expansion_confidence() -> None:
    assert round(confidence("DIRECTIONAL_EXPANSION"), 4) == round((0.6 + 0.4 + 0.7) / 3, 4)


def test_directional_drift_confidence() -> None:
    assert round(confidence("DIRECTIONAL_DRIFT"), 4) == round((0.6 + 0.6 + 0.7) / 3, 4)


def test_neutral_compression_confidence() -> None:
    assert round(confidence("NEUTRAL_COMPRESSION"), 4) == round((0.6 + 0.4 + 0.7) / 3, 4)


def test_complex_consolidation_confidence() -> None:
    assert round(confidence("COMPLEX_CONSOLIDATION"), 4) == round((0.7 + 0.6 + 0.5 + 0.7) / 4, 4)


def test_volatile_rotation_confidence() -> None:
    assert round(confidence("VOLATILE_ROTATION"), 4) == round((0.8 + 0.4 + 0.6 + 0.7) / 4, 4)


def test_unclassified_confidence() -> None:
    assert confidence("UNCLASSIFIED") == 0.0
