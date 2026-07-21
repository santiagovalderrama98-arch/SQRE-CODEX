from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    build_profile_reviews,
)
from sqre.h4_transition_scenario_sensitive_review.loader import load_scenario_sensitive_profiles
from sqre.h4_transition_scenario_sensitive_review.profile_selector import select_review_profiles
from sqre.h4_transition_scenario_sensitive_review.transition_family_review import (
    build_transition_family_sensitivity_summary,
)


def test_transition_family_sensitivity_summary_aggregates_profiles(tmp_path: Path):
    dispersion_dir, _ = write_transition_sensitive_inputs(tmp_path)
    config = H4TransitionScenarioSensitiveReviewConfig()
    reviews = build_profile_reviews(select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config), config)

    summaries = build_transition_family_sensitivity_summary(reviews)

    family = next(row for row in summaries if row.group_value == "DIRECTIONAL_TO_DIRECTIONAL")
    assert family.profile_count == 2
    assert family.focus_profile_count == 2
