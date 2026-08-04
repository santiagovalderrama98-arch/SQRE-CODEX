from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.regime_context_review import (
    build_regime_distribution_review,
)


def test_regime_distribution_classifies_sample_constrained():
    profiles = pd.DataFrame(
        [
            {"H4_Transition_Label": "A -> B", "D1_Regime_Label": "EXPANSION", "Context_Row_Count": 3},
            {"H4_Transition_Label": "A -> B", "D1_Regime_Label": "CONSOLIDATION", "Context_Row_Count": 2},
        ]
    )

    review = build_regime_distribution_review(profiles, H4D1SameTimeContextualTransitionReviewConfig())

    assert set(review["Distribution_Class"]) == {"D1_CONTEXT_SAMPLE_CONSTRAINED"}
