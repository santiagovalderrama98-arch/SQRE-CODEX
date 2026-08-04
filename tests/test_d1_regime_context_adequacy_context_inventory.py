from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.d1_context_inventory import (
    build_d1_context_inventory,
    classify_d1_context_adequacy,
)
from tests.d1_regime_context_adequacy_test_utils import write_contextual_transition_inputs


def test_context_inventory_groups_d1_contexts(tmp_path):
    input_dir = tmp_path / "contextual"
    profiles = write_contextual_transition_inputs(input_dir)

    frame = build_d1_context_inventory(profiles, D1RegimeContextAdequacyReviewConfig())

    assert set(frame["D1_Context_Adequacy_Class"]) >= {
        "D1_CONTEXT_ADEQUATE_FOR_RESEARCH",
        "D1_CONTEXT_SAMPLE_CONSTRAINED",
    }
    assert int(frame["Aligned_H4_Transition_Row_Count"].sum()) == 35


def test_context_inventory_classifies_over_fragmented_context():
    assert classify_d1_context_adequacy(ready_count=0, low_count=5, profile_count=5, row_count=12) == (
        "D1_CONTEXT_OVER_FRAGMENTED"
    )
