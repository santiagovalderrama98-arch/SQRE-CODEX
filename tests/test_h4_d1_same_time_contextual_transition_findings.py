from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.readiness_classifier import build_summary


def test_findings_produce_readiness_flag():
    profiles = pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A -> B",
                "D1_Market_State": "TREND",
                "D1_Regime_Label": "EXPANSION",
                "Context_Row_Count": 25,
                "Context_Sample_Adequacy_Class": "RESEARCH_READY_CONTEXT_SAMPLE",
                "Contextual_Review_Class": "SAME_TIME_CONTEXT_RESEARCH_READY",
            }
        ]
    )
    concentration = pd.DataFrame([{"Transition_Context_Distribution_Class": "D1_CONTEXT_CONCENTRATED"}])

    summary = build_summary(profiles, concentration, H4D1SameTimeContextualTransitionReviewConfig())

    assert summary.h4_d1_contextual_transition_readiness_flag == "READY_FOR_H4_D1_ALIGNED_OUTCOME_RESEARCH"
