from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.d1_context_sample_adequacy_review import (
    build_d1_context_sample_adequacy_review,
)


def test_d1_context_sample_adequacy_computes_ready_ratio():
    inventory = pd.DataFrame(
        [
            {
                "D1_Context_ID": "D1_CONTEXT_000001",
                "D1_Market_State": "D1_TREND",
                "D1_Regime_Label": "D1_EXPANSION",
                "Aligned_H4_Transition_Row_Count": 20,
                "Distinct_H4_Transition_Count": 2,
                "Research_Ready_Context_Count": 1,
                "Low_Or_Insufficient_Context_Count": 3,
                "D1_Context_Adequacy_Class": "D1_CONTEXT_PARTIALLY_ADEQUATE",
            }
        ]
    )

    review = build_d1_context_sample_adequacy_review(inventory)

    assert review.loc[0, "Context_Research_Ready_Ratio"] == 0.25
    assert review.loc[0, "D1_Context_Adequacy_Class"] == "D1_CONTEXT_PARTIALLY_ADEQUATE"
