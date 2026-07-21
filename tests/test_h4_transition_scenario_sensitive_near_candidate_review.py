from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    build_profile_reviews,
)
from sqre.h4_transition_scenario_sensitive_review.loader import load_scenario_sensitive_profiles
from sqre.h4_transition_scenario_sensitive_review.near_candidate_review import (
    build_focus_profile_review,
    build_near_aggregation_candidates,
)
from sqre.h4_transition_scenario_sensitive_review.profile_selector import select_review_profiles


def test_near_candidate_and_focus_outputs_can_be_built(tmp_path: Path):
    dispersion_dir, _ = write_transition_sensitive_inputs(tmp_path)
    config = H4TransitionScenarioSensitiveReviewConfig()
    reviews = build_profile_reviews(select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config), config)

    near = build_near_aggregation_candidates(reviews)
    focus = build_focus_profile_review(reviews)

    assert len(near) == 1
    assert near[0].near_candidate_rationale
    assert len(focus) == 2


def test_near_candidate_and_focus_outputs_can_be_empty(tmp_path: Path):
    dispersion_dir, _ = write_transition_sensitive_inputs(tmp_path)
    config = H4TransitionScenarioSensitiveReviewConfig(focus_transitions=("ABSENT -> STATE",))
    reviews = build_profile_reviews(select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config), config)

    assert build_focus_profile_review(reviews) == []
    assert build_near_aggregation_candidates([]) == []
