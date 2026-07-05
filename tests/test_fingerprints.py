from __future__ import annotations

from sqre.market_structure.fingerprints import FingerprintBuilder
from sqre.market_structure.models import StructuralMetrics


def test_fingerprint_builder_clamps_metrics_to_normalized_range() -> None:
    metrics = StructuralMetrics(
        event_count=10,
        pivot_count=4,
        swing_count=2,
        large_candle_count=1,
        small_candle_count=1,
        range_expansion_count=2,
        range_contraction_count=1,
        leg_count=4,
        up_leg_count=2,
        down_leg_count=2,
        direction_changes=3,
        gross_distance_pips=40,
        net_displacement_pips=12,
        average_leg_distance_pips=10,
        max_leg_distance_pips=14,
        min_leg_distance_pips=8,
        persistence_index=1.5,
        structural_complexity=0.5,
        structural_stability=-0.2,
        structural_efficiency=0.7,
        event_density=0.9,
        structural_volatility=2.0,
        structural_symmetry=0.8,
        structural_confidence=0.6,
    )

    fingerprint = FingerprintBuilder().build("STR_000001", metrics)

    assert fingerprint.structure_id == "STR_000001"
    assert fingerprint.persistence == 1.0
    assert fingerprint.stability == 0.0
    assert fingerprint.volatility == 1.0
