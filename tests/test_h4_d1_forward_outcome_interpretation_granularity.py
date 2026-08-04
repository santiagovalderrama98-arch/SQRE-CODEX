import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.context_granularity_review import (
    best_supported_granularity,
    build_context_granularity_utility_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.profile_interpretability_review import (
    build_profile_interpretability_review,
)
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_phase_7515_inputs


def test_context_granularity_utility_identifies_best_supported_granularity(tmp_path):
    forward_dir = tmp_path / "forward"
    write_phase_7515_inputs(forward_dir)
    profiles = pd.read_csv(forward_dir / "h4_d1_forward_outcome_profiles.csv")
    interpretability = build_profile_interpretability_review(profiles, H4D1ForwardOutcomeInterpretationReviewConfig())

    review = build_context_granularity_utility_review(interpretability)

    assert best_supported_granularity(review) == "H4_TRANSITION_ONLY"
    assert "BROAD_CONTEXT_MORE_USEFUL" in set(review["Context_Granularity_Utility_Class"])
