from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.outcome_dispersion_review import classify_outcome_dispersion


def test_dispersion_review_classifies_high_and_low_dispersion():
    assert classify_outcome_dispersion(2.0) == "LOW_OUTCOME_DISPERSION"
    assert classify_outcome_dispersion(20.0) == "HIGH_OUTCOME_DISPERSION"
