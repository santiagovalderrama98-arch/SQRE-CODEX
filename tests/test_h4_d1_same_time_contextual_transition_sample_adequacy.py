from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.sample_adequacy_review import (
    build_sample_adequacy_review,
)


def test_sample_adequacy_review_marks_ready_and_insufficient_contexts():
    profiles = pd.DataFrame(
        [
            {
                "Context_Profile_ID": "P1",
                "H4_Transition_Label": "A -> B",
                "D1_Market_State": "TREND",
                "D1_Regime_Label": "EXPANSION",
                "Context_Row_Count": 20,
                "Context_Sample_Adequacy_Class": "RESEARCH_READY_CONTEXT_SAMPLE",
            },
            {
                "Context_Profile_ID": "P2",
                "H4_Transition_Label": "B -> A",
                "D1_Market_State": "RANGE",
                "D1_Regime_Label": "CONSOLIDATION",
                "Context_Row_Count": 1,
                "Context_Sample_Adequacy_Class": "LOW_CONTEXT_SAMPLE",
            },
        ]
    )

    review = build_sample_adequacy_review(profiles, H4D1SameTimeContextualTransitionReviewConfig())

    assert list(review["Ready_For_Outcome_Research"]) == ["TRUE", "FALSE"]
