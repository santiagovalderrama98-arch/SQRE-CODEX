"""Review H4 transition distribution across D1 regime labels."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.d1_context_distribution_review import _build_distribution


REGIME_DISTRIBUTION_COLUMNS = [
    "H4_Transition_Label",
    "D1_Regime_Label",
    "Context_Row_Count",
    "Transition_Total_Count",
    "Context_Share_Within_Transition",
    "Distribution_Class",
    "Distribution_Diagnostic",
]


def build_regime_distribution_review(
    profiles: pd.DataFrame,
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> pd.DataFrame:
    return _build_distribution(
        profiles,
        context_column="D1_Regime_Label",
        output_columns=REGIME_DISTRIBUTION_COLUMNS,
        config=config,
    )
