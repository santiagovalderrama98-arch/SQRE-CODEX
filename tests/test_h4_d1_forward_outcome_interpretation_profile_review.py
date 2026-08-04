import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.profile_interpretability_review import (
    build_profile_interpretability_review,
)
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_phase_7515_inputs


def test_profile_interpretability_classifies_interpretable_sample_and_high_dispersion(tmp_path):
    forward_dir = tmp_path / "forward"
    write_phase_7515_inputs(forward_dir)
    profiles = pd.read_csv(forward_dir / "h4_d1_forward_outcome_profiles.csv")

    review = build_profile_interpretability_review(profiles, H4D1ForwardOutcomeInterpretationReviewConfig())
    classes = dict(zip(review["Outcome_Profile_ID"], review["Outcome_Interpretability_Class"]))

    assert classes["P1"] == "INTERPRETABLE_OUTCOME_PROFILE"
    assert classes["P6"] == "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED"
    assert classes["P7"] == "NOT_INTERPRETABLE_HIGH_DISPERSION"
