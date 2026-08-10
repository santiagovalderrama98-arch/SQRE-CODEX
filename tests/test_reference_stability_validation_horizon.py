from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.horizon_stability_review import build_horizon_stability_review
from tests.test_reference_stability_validation_loader import reference_store_frame


def test_horizon_review_classifies_stable_and_unstable_horizons():
    review = build_horizon_stability_review(ReferenceStabilityValidationConfig(), reference_store_frame())

    assert "STABLE_ACROSS_HORIZONS" in set(review["Horizon_Stability_Class"])
    assert "HORIZON_UNSTABLE" in set(review["Horizon_Stability_Class"])
