from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.reference_population_review import build_reference_population_review
from tests.test_reference_stability_validation_loader import reference_store_frame


def test_population_review_counts_core_and_supporting_references():
    review = build_reference_population_review(ReferenceStabilityValidationConfig(), reference_store_frame(), False)
    row = review.iloc[0]

    assert row["Reference_Count"] == 3
    assert row["Core_Reference_Count"] == 2
    assert row["Supporting_Reference_Count"] == 1
    assert row["Reference_Population_Class"] == "REFERENCE_POPULATION_AVAILABLE"
