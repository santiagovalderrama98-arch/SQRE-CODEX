from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.d1_context_distribution_review import (
    build_market_state_distribution_review,
)


def test_market_state_distribution_classifies_concentration():
    profiles = pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A -> B",
                "D1_Market_State": "TREND",
                "Context_Row_Count": 16,
            },
            {
                "H4_Transition_Label": "A -> B",
                "D1_Market_State": "RANGE",
                "Context_Row_Count": 4,
            },
        ]
    )

    review = build_market_state_distribution_review(profiles, H4D1SameTimeContextualTransitionReviewConfig())

    assert review.loc[review["D1_Market_State"] == "TREND", "Distribution_Class"].iloc[0] == "D1_CONTEXT_CONCENTRATED"
