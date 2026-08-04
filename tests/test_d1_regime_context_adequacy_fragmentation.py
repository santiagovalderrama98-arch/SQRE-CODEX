from __future__ import annotations

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.d1_fragmentation_review import build_fragmentation_review
from tests.d1_regime_context_adequacy_test_utils import write_contextual_transition_inputs


def test_fragmentation_review_classifies_high_fragmentation(tmp_path):
    input_dir = tmp_path / "contextual"
    profiles = write_contextual_transition_inputs(input_dir)
    concentration = __import__("pandas").DataFrame(
        [
            {
                "H4_Transition_Label": "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT",
                "Dominant_D1_Market_State": "D1_RANGE",
                "Dominant_D1_Market_State_Share": 0.64,
            }
        ]
    )

    review = build_fragmentation_review(profiles, concentration, D1RegimeContextAdequacyReviewConfig())
    row = review[review["H4_Transition_Label"] == "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT"].iloc[0]

    assert row["D1_Fragmentation_Class"] == "HIGH_D1_CONTEXT_FRAGMENTATION"
    assert row["Low_Or_Insufficient_Context_Count"] == 3
