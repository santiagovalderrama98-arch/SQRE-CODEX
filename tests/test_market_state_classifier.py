from __future__ import annotations

from datetime import datetime, timedelta

from sqre.market_states.classifier import MarketStateClassifier
from sqre.market_states.models import StructuralInput


def structure(**overrides) -> StructuralInput:
    data = {
        "structure_id": "STR_000001",
        "symbol": "EURUSD",
        "timeframe": "M5",
        "start_time": datetime(2026, 1, 1),
        "end_time": datetime(2026, 1, 1) + timedelta(minutes=5),
        "direction": "UP",
        "lifecycle_stage": "MATURITY",
        "persistence_index": 0.2,
        "structural_complexity": 0.2,
        "structural_stability": 0.7,
        "structural_efficiency": 0.4,
        "event_density": 0.2,
        "structural_volatility": 0.2,
        "structural_symmetry": 0.8,
        "structural_confidence": 0.7,
    }
    data.update(overrides)
    return StructuralInput(**data)


def classify(structural_input: StructuralInput) -> str:
    return MarketStateClassifier().classify(structural_input).market_state


def test_classifies_low_quality_structure() -> None:
    assert classify(structure(structural_confidence=0.4)) == "LOW_QUALITY_STRUCTURE"


def test_classifies_directional_expansion() -> None:
    result = MarketStateClassifier().classify(
        structure(
            direction="UP",
            persistence_index=0.6,
            structural_efficiency=0.7,
            structural_confidence=0.8,
        )
    )

    assert result.market_state == "DIRECTIONAL_EXPANSION"
    assert result.classification_rule == "directional_expansion_rule"


def test_classifies_directional_displacement() -> None:
    result = MarketStateClassifier().classify(
        structure(
            direction="DOWN",
            persistence_index=0.3,
            structural_efficiency=0.7,
            structural_confidence=0.6,
        )
    )

    assert result.market_state == "DIRECTIONAL_DISPLACEMENT"
    assert result.classification_rule == "directional_displacement_rule"


def test_directional_expansion_priority_wins_over_displacement() -> None:
    result = MarketStateClassifier().classify(
        structure(
            direction="UP",
            persistence_index=0.7,
            structural_efficiency=0.7,
            structural_confidence=0.8,
        )
    )

    assert result.market_state == "DIRECTIONAL_EXPANSION"
    assert result.classification_rule == "directional_expansion_rule"


def test_classifies_directional_drift() -> None:
    assert (
        classify(
            structure(
                direction="DOWN",
                persistence_index=0.45,
                structural_efficiency=0.4,
                structural_confidence=0.75,
            )
        )
        == "DIRECTIONAL_DRIFT"
    )


def test_classifies_neutral_compression() -> None:
    assert (
        classify(
            structure(
                direction="NEUTRAL",
                persistence_index=0.2,
                structural_efficiency=0.2,
                structural_confidence=0.7,
            )
        )
        == "NEUTRAL_COMPRESSION"
    )


def test_classifies_complex_consolidation() -> None:
    assert (
        classify(
            structure(
                direction="NEUTRAL",
                structural_complexity=0.75,
                structural_efficiency=0.2,
                event_density=0.6,
                persistence_index=0.7,
                structural_confidence=0.8,
            )
        )
        == "COMPLEX_CONSOLIDATION"
    )


def test_classifies_volatile_rotation() -> None:
    assert (
        classify(
            structure(
                structural_volatility=0.8,
                persistence_index=0.3,
                structural_efficiency=0.3,
                structural_confidence=0.7,
            )
        )
        == "VOLATILE_ROTATION"
    )


def test_returns_unclassified_when_no_rule_applies() -> None:
    assert classify(structure(persistence_index=0.1, structural_efficiency=0.55, structural_confidence=0.8)) == "UNCLASSIFIED"


def test_classification_priority_low_quality_wins() -> None:
    assert (
        classify(
            structure(
                direction="UP",
                persistence_index=0.8,
                structural_efficiency=0.8,
                structural_confidence=0.4,
            )
        )
        == "LOW_QUALITY_STRUCTURE"
    )
