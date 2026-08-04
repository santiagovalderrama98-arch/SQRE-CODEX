import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.directional_behavior_review import (
    build_directional_behavior_review,
)
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_phase_7515_inputs


def test_directional_behavior_detects_up_down_and_mixed(tmp_path):
    forward_dir = tmp_path / "forward"
    write_phase_7515_inputs(forward_dir)
    profiles = pd.read_csv(forward_dir / "h4_d1_forward_outcome_profiles.csv")

    review = build_directional_behavior_review(profiles, H4D1ForwardOutcomeInterpretationReviewConfig())
    classes = dict(zip(review["Outcome_Profile_ID"], review["Directional_Behavior_Class"]))

    assert classes["P1"] == "OBSERVED_UPWARD_FOLLOW_THROUGH_DOMINANCE"
    assert classes["P4"] == "OBSERVED_DOWNWARD_FOLLOW_THROUGH_DOMINANCE"
    assert classes["P5"] == "OBSERVED_MIXED_DIRECTIONAL_BEHAVIOR"
