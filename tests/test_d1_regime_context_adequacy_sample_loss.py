from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.h4_transition_sample_loss_review import build_sample_loss_review


def test_sample_loss_review_detects_extreme_sample_loss():
    profiles = pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A -> B",
                "Transition_Total_Count": 30,
                "Context_Sample_Adequacy_Class": "LOW_CONTEXT_SAMPLE",
            },
            {
                "H4_Transition_Label": "A -> B",
                "Transition_Total_Count": 30,
                "Context_Sample_Adequacy_Class": "INSUFFICIENT_CONTEXT_SAMPLE",
            },
        ]
    )

    review = build_sample_loss_review(profiles, D1RegimeContextAdequacyReviewConfig())

    assert review.loc[0, "Raw_Transition_Sample_Adequacy"] == "RAW_TRANSITION_SAMPLE_ADEQUATE"
    assert review.loc[0, "Transition_Sample_Loss_Class"] == "EXTREME_SAMPLE_LOSS"
