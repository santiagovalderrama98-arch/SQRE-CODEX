"""Structural fingerprints."""

from __future__ import annotations

from sqre.market_structure.metrics import clamp
from sqre.market_structure.models import StructuralFingerprint, StructuralMetrics


class FingerprintBuilder:
    """Build normalized structural fingerprints from metrics."""

    def build(self, structure_id: str, metrics: StructuralMetrics) -> StructuralFingerprint:
        return StructuralFingerprint(
            structure_id=structure_id,
            persistence=clamp(metrics.persistence_index),
            complexity=clamp(metrics.structural_complexity),
            stability=clamp(metrics.structural_stability),
            efficiency=clamp(metrics.structural_efficiency),
            density=clamp(metrics.event_density),
            volatility=clamp(metrics.structural_volatility),
            symmetry=clamp(metrics.structural_symmetry),
            confidence=clamp(metrics.structural_confidence),
        )
