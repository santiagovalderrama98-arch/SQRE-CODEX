import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.directional_behavior_review import (
    build_directional_behavior_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.horizon_stability_review import build_horizon_stability_review
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_phase_7515_inputs


def test_horizon_stability_detects_stable_and_unstable_contexts(tmp_path):
    forward_dir = tmp_path / "forward"
    write_phase_7515_inputs(forward_dir)
    profiles = pd.read_csv(forward_dir / "h4_d1_forward_outcome_profiles.csv")
    directional = build_directional_behavior_review(profiles, H4D1ForwardOutcomeInterpretationReviewConfig())

    review = build_horizon_stability_review(directional)

    assert "STABLE_ACROSS_HORIZONS" in set(review["Horizon_Stability_Class"])
    assert "UNSTABLE_ACROSS_HORIZONS" in set(review["Horizon_Stability_Class"])
