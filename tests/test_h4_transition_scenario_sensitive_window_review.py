from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    build_profile_reviews,
)
from sqre.h4_transition_scenario_sensitive_review.loader import load_scenario_sensitive_profiles
from sqre.h4_transition_scenario_sensitive_review.profile_selector import select_review_profiles
from sqre.h4_transition_scenario_sensitive_review.transition_window_review import (
    build_forward_window_sensitivity_summary,
)


def test_forward_window_sensitivity_summary_aggregates_profiles(tmp_path: Path):
    dispersion_dir, _ = write_transition_sensitive_inputs(tmp_path)
    config = H4TransitionScenarioSensitiveReviewConfig()
    reviews = build_profile_reviews(select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config), config)

    summaries = build_forward_window_sensitivity_summary(reviews)

    fw3 = next(row for row in summaries if row.forward_window == 3)
    assert fw3.profile_count == 2
    assert fw3.focus_profile_count == 1
