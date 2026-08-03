from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.contextual_concentration_review import (
    build_context_concentration_review,
)


def test_concentration_review_identifies_dominant_state_and_regime():
    profiles = pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A -> B",
                "D1_Market_State": "TREND",
                "D1_Regime_Label": "EXPANSION",
                "Context_Row_Count": 16,
            },
            {
                "H4_Transition_Label": "A -> B",
                "D1_Market_State": "RANGE",
                "D1_Regime_Label": "CONSOLIDATION",
                "Context_Row_Count": 4,
            },
        ]
    )

    review = build_context_concentration_review(profiles, H4D1SameTimeContextualTransitionReviewConfig())

    row = review.iloc[0]
    assert row["Dominant_D1_Market_State"] == "TREND"
    assert row["Dominant_D1_Regime_Label"] == "EXPANSION"
    assert row["Transition_Context_Distribution_Class"] == "D1_CONTEXT_CONCENTRATED"
