"""State confidence calculations for Market States."""

from __future__ import annotations

from sqre.market_states.models import StateClassificationResult, StructuralInput


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(value, maximum))


class StateConfidenceCalculator:
    """Calculate how strongly a structure fits its assigned Market State."""

    def calculate(self, structure: StructuralInput, classification: StateClassificationResult) -> float:
        state = classification.market_state
        if state == "LOW_QUALITY_STRUCTURE":
            return clamp(1 - structure.structural_confidence)
        if state == "DIRECTIONAL_EXPANSION":
            return self._average(
                structure.persistence_index,
                structure.structural_efficiency,
                structure.structural_confidence,
            )
        if state == "DIRECTIONAL_DISPLACEMENT":
            return self._average(
                structure.structural_efficiency,
                structure.structural_confidence,
                1 - abs(structure.persistence_index - 0.50),
            )
        if state == "DIRECTIONAL_DRIFT":
            return self._average(
                structure.persistence_index,
                1 - structure.structural_efficiency,
                structure.structural_confidence,
            )
        if state == "NEUTRAL_COMPRESSION":
            return self._average(
                1 - structure.structural_efficiency,
                1 - structure.persistence_index,
                structure.structural_confidence,
            )
        if state == "COMPLEX_CONSOLIDATION":
            return self._average(
                structure.structural_complexity,
                1 - structure.structural_efficiency,
                structure.event_density,
                structure.structural_confidence,
            )
        if state == "VOLATILE_ROTATION":
            return self._average(
                structure.structural_volatility,
                1 - structure.persistence_index,
                1 - structure.structural_efficiency,
                structure.structural_confidence,
            )
        return 0.0

    def _average(self, *values: float) -> float:
        if not values:
            return 0.0
        return clamp(sum(values) / len(values))
