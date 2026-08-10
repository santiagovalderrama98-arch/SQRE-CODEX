from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.granularity_stability_review import build_granularity_stability_review
from tests.test_reference_stability_validation_loader import reference_store_frame


def test_granularity_review_classifies_fragmented_contexts():
    review = build_granularity_stability_review(ReferenceStabilityValidationConfig(), reference_store_frame())

    assert "FRAGMENTED_GRANULARITY_CONTEXT" in set(review["Granularity_Stability_Class"])
