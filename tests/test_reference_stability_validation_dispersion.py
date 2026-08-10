from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.dispersion_stability_review import build_dispersion_stability_review
from tests.test_reference_stability_validation_loader import reference_store_frame


def test_dispersion_review_classifies_stable_usable_and_high_groups():
    review = build_dispersion_stability_review(ReferenceStabilityValidationConfig(), reference_store_frame())

    assert "STABLE_DISPERSION" in set(review["Dispersion_Stability_Class"])
    assert "USABLE_DISPERSION" in set(review["Dispersion_Stability_Class"])
    assert "HIGH_DISPERSION" in set(review["Dispersion_Stability_Class"])
