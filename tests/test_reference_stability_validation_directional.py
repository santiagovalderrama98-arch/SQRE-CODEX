from __future__ import annotations

from sqre.reference_stability_validation.directional_consistency_review import build_directional_consistency_review
from tests.test_reference_stability_validation_loader import reference_store_frame


def test_directional_review_handles_mixed_directional_behavior():
    review = build_directional_consistency_review(reference_store_frame())

    assert "DIRECTIONAL_BEHAVIOR_UNSTABLE" in set(review["Directional_Consistency_Class"])
