from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    build_profile_reviews,
)
from sqre.h4_transition_scenario_sensitive_review.loader import load_scenario_sensitive_profiles
from sqre.h4_transition_scenario_sensitive_review.profile_selector import select_review_profiles
from sqre.h4_transition_scenario_sensitive_review.transition_state_review import (
    build_source_state_sensitivity_summary,
    build_target_state_sensitivity_summary,
)


def test_source_and_target_state_summaries_aggregate_profiles(tmp_path: Path):
    dispersion_dir, _ = write_transition_sensitive_inputs(tmp_path)
    config = H4TransitionScenarioSensitiveReviewConfig()
    reviews = build_profile_reviews(select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config), config)

    source = build_source_state_sensitivity_summary(reviews)
    target = build_target_state_sensitivity_summary(reviews)

    assert next(row for row in source if row.group_value == "DIRECTIONAL_DISPLACEMENT").profile_count == 2
    assert next(row for row in target if row.group_value == "DIRECTIONAL_EXPANSION").profile_count == 1
