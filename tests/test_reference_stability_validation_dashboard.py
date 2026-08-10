from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.dashboard_reference_stability_review import (
    build_dashboard_reference_stability_review,
)
from tests.test_reference_stability_validation_loader import dashboard_cards_frame


def test_dashboard_reference_stability_review_handles_reference_cards():
    review = build_dashboard_reference_stability_review(ReferenceStabilityValidationConfig(), dashboard_cards_frame())
    row = review.iloc[0]

    assert row["Reference_Card_Count"] == 5
    assert row["Dashboard_Reference_Stability_Class"] == "DASHBOARD_REFERENCES_STABLE_FOR_REVIEW"
