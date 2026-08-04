from __future__ import annotations

from sqre.d1_regime_context_adequacy_review.aggregation_candidate_review import build_aggregation_candidate_review
from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from tests.d1_regime_context_adequacy_test_utils import write_contextual_transition_inputs


def test_aggregation_candidates_identify_constrained_d1_groups(tmp_path):
    profiles = write_contextual_transition_inputs(tmp_path / "contextual")

    review = build_aggregation_candidate_review(profiles, D1RegimeContextAdequacyReviewConfig())

    assert "REVIEW_D1_MARKET_STATE_AGGREGATION" in set(review["Aggregation_Candidate_Class"])
    assert "D1_MARKET_STATE_GROUPING_RESEARCH" in set(review["Recommended_Follow_Up"])
