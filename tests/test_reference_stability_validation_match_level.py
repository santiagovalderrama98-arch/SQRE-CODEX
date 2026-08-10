from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.match_level_stability_review import build_match_level_stability_review
from tests.test_reference_stability_validation_loader import query_results_frame


def test_match_level_review_identifies_fallback_dependent_usage():
    review = build_match_level_stability_review(ReferenceStabilityValidationConfig(), query_results_frame())

    assert "STABLE_MATCH_LEVEL_USAGE" in set(review["Match_Level_Stability_Class"])
    assert "FALLBACK_DEPENDENT_MATCH_USAGE" in set(review["Match_Level_Stability_Class"])
