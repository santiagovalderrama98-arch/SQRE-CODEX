from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.sample_adequacy_review import build_sample_adequacy_review
from tests.test_reference_stability_validation_loader import reference_store_frame


def test_sample_adequacy_review_classifies_stable_usable_and_low_groups():
    review = build_sample_adequacy_review(ReferenceStabilityValidationConfig(), reference_store_frame())

    assert "STABLE_SAMPLE_SIZE" in set(review["Sample_Adequacy_Class"])
    assert "USABLE_SAMPLE_SIZE" in set(review["Sample_Adequacy_Class"])
    assert "LOW_SAMPLE_SIZE" in set(review["Sample_Adequacy_Class"])
