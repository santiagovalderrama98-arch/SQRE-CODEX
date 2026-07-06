"""Rule-based Market State classification."""

from __future__ import annotations

from sqre.market_states.config import MarketStatesConfig
from sqre.market_states.models import StateClassificationResult, StructuralInput


class MarketStateClassifier:
    """Classify one Market Structure into one descriptive Market State."""

    DIRECTIONAL_DIRECTIONS = {"UP", "DOWN"}

    def __init__(self, config: MarketStatesConfig | None = None) -> None:
        self.config = config or MarketStatesConfig()

    def classify(self, structure: StructuralInput) -> StateClassificationResult:
        if self._is_low_quality_structure(structure):
            return StateClassificationResult("LOW_QUALITY_STRUCTURE", "low_quality_structure_rule")
        if self._is_directional_expansion(structure):
            return StateClassificationResult("DIRECTIONAL_EXPANSION", "directional_expansion_rule")
        if self._is_directional_displacement(structure):
            return StateClassificationResult("DIRECTIONAL_DISPLACEMENT", "directional_displacement_rule")
        if self._is_complex_consolidation(structure):
            return StateClassificationResult("COMPLEX_CONSOLIDATION", "complex_consolidation_rule")
        if self._is_volatile_rotation(structure):
            return StateClassificationResult("VOLATILE_ROTATION", "volatile_rotation_rule")
        if self._is_neutral_compression(structure):
            return StateClassificationResult("NEUTRAL_COMPRESSION", "neutral_compression_rule")
        if self._is_directional_drift(structure):
            return StateClassificationResult("DIRECTIONAL_DRIFT", "directional_drift_rule")
        return StateClassificationResult("UNCLASSIFIED", "unclassified_rule")

    def _is_low_quality_structure(self, structure: StructuralInput) -> bool:
        return structure.structural_confidence < self.config.low_quality_confidence_threshold

    def _is_directional_expansion(self, structure: StructuralInput) -> bool:
        return (
            structure.direction in self.DIRECTIONAL_DIRECTIONS
            and structure.persistence_index >= self.config.directional_expansion_persistence_threshold
            and structure.structural_efficiency >= self.config.directional_expansion_efficiency_threshold
            and structure.structural_confidence >= self.config.directional_expansion_confidence_threshold
        )

    def _is_directional_displacement(self, structure: StructuralInput) -> bool:
        return (
            structure.direction in self.DIRECTIONAL_DIRECTIONS
            and structure.structural_efficiency >= self.config.directional_displacement_efficiency_threshold
            and structure.structural_confidence >= self.config.directional_displacement_confidence_threshold
        )

    def _is_directional_drift(self, structure: StructuralInput) -> bool:
        return (
            structure.direction in self.DIRECTIONAL_DIRECTIONS
            and structure.persistence_index >= self.config.directional_drift_persistence_threshold
            and structure.structural_efficiency < self.config.directional_drift_efficiency_threshold
            and structure.structural_confidence >= self.config.directional_drift_confidence_threshold
        )

    def _is_neutral_compression(self, structure: StructuralInput) -> bool:
        return (
            structure.direction == "NEUTRAL"
            and structure.structural_efficiency < self.config.neutral_compression_efficiency_threshold
            and structure.persistence_index < self.config.neutral_compression_persistence_threshold
        )

    def _is_complex_consolidation(self, structure: StructuralInput) -> bool:
        return (
            structure.structural_complexity >= self.config.complex_consolidation_complexity_threshold
            and structure.structural_efficiency < self.config.complex_consolidation_efficiency_threshold
            and structure.event_density >= self.config.complex_consolidation_density_threshold
        )

    def _is_volatile_rotation(self, structure: StructuralInput) -> bool:
        return (
            structure.structural_volatility >= self.config.volatile_rotation_volatility_threshold
            and structure.persistence_index < self.config.volatile_rotation_persistence_threshold
            and structure.structural_efficiency < self.config.volatile_rotation_efficiency_threshold
        )
