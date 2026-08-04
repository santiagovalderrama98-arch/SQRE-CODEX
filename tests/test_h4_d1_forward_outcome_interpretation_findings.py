import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.context_granularity_review import (
    build_context_granularity_utility_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.directional_behavior_review import (
    build_directional_behavior_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.findings import build_summary
from sqre.h4_d1_forward_outcome_interpretation_review.horizon_stability_review import build_horizon_stability_review
from sqre.h4_d1_forward_outcome_interpretation_review.profile_interpretability_review import (
    build_profile_interpretability_review,
)
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_phase_7515_inputs


def test_findings_produce_ready_flag_when_interpretable_profiles_exist(tmp_path):
    forward_dir = tmp_path / "forward"
    write_phase_7515_inputs(forward_dir)
    profiles = pd.read_csv(forward_dir / "h4_d1_forward_outcome_profiles.csv")
    config = H4D1ForwardOutcomeInterpretationReviewConfig()
    interpretability = build_profile_interpretability_review(profiles, config)
    directional = build_directional_behavior_review(profiles, config)
    horizon = build_horizon_stability_review(directional)
    granularity = build_context_granularity_utility_review(interpretability)

    summary = build_summary(interpretability, directional, horizon, granularity, config)

    assert summary.h4_d1_forward_outcome_interpretation_readiness_flag == "READY_FOR_RESEARCH_REFERENCE_STORE_DESIGN"
    assert summary.interpretable_profile_count == 3
