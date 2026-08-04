import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.excursion_behavior_review import (
    build_excursion_behavior_review,
)
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_phase_7515_inputs


def test_excursion_behavior_classifies_upside_downside_and_balanced(tmp_path):
    forward_dir = tmp_path / "forward"
    write_phase_7515_inputs(forward_dir)
    profiles = pd.read_csv(forward_dir / "h4_d1_forward_outcome_profiles.csv")

    review = build_excursion_behavior_review(profiles, H4D1ForwardOutcomeInterpretationReviewConfig())
    classes = dict(zip(review["Outcome_Profile_ID"], review["Excursion_Behavior_Class"]))

    assert classes["P1"] == "UPSIDE_EXCURSION_DOMINANT"
    assert classes["P4"] == "DOWNSIDE_EXCURSION_DOMINANT"
    assert classes["P5"] == "BALANCED_EXCURSION_BEHAVIOR"
