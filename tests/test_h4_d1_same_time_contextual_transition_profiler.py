from __future__ import annotations

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.contextual_transition_profiler import (
    build_contextual_transition_profiles,
)
from sqre.h4_d1_same_time_contextual_transition_review.loader import load_transition_alignment
from tests.h4_d1_same_time_contextual_transition_test_utils import write_transition_alignment


def test_profiler_groups_transition_state_regime_and_computes_shares(tmp_path):
    write_transition_alignment(tmp_path)
    frame = load_transition_alignment(tmp_path)

    profiles = build_contextual_transition_profiles(frame, H4D1SameTimeContextualTransitionReviewConfig())

    assert len(profiles) == 2
    ready = profiles.loc[profiles["Context_Row_Count"] == 18].iloc[0]
    assert ready["Context_Share_Of_Total"] == 0.75
    assert ready["Context_Share_Within_Transition"] == 1.0
    assert ready["Context_Sample_Adequacy_Class"] == "MODERATE_CONTEXT_SAMPLE"
