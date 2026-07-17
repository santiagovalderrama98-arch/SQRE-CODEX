from pathlib import Path

from test_h4_scenario_sensitive_state_review_loader import write_sensitive_inputs
from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig
from sqre.h4_scenario_sensitive_state_review.h4_scenario_sensitive_state_review_pipeline import build_profile_reviews
from sqre.h4_scenario_sensitive_state_review.loader import load_scenario_sensitive_profiles
from sqre.h4_scenario_sensitive_state_review.near_candidate_review import build_near_aggregation_candidates
from sqre.h4_scenario_sensitive_state_review.profile_selector import select_review_profiles


def test_near_candidate_output_can_be_populated_or_empty(tmp_path: Path):
    dispersion_dir, _ = write_sensitive_inputs(tmp_path)
    config = H4ScenarioSensitiveStateReviewConfig()
    profiles = select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config)
    reviews = build_profile_reviews(profiles, config)

    near = build_near_aggregation_candidates(reviews)

    assert [row.condition_label for row in near] == ["DIRECTIONAL_EXPANSION", "VOLATILE_ROTATION"]
