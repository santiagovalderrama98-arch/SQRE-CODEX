from pathlib import Path

from test_h4_scenario_sensitive_state_review_loader import write_sensitive_inputs
from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig
from sqre.h4_scenario_sensitive_state_review.h4_scenario_sensitive_state_review_pipeline import build_profile_reviews
from sqre.h4_scenario_sensitive_state_review.loader import load_scenario_sensitive_profiles
from sqre.h4_scenario_sensitive_state_review.profile_selector import select_review_profiles
from sqre.h4_scenario_sensitive_state_review.state_window_review import (
    build_state_sensitivity_summary,
    build_window_sensitivity_summary,
)


def test_state_and_window_summaries_aggregate_profiles(tmp_path: Path):
    dispersion_dir, _ = write_sensitive_inputs(tmp_path)
    config = H4ScenarioSensitiveStateReviewConfig()
    profiles = select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config)
    reviews = build_profile_reviews(profiles, config)

    state_rows = build_state_sensitivity_summary(reviews)
    window_rows = build_window_sensitivity_summary(reviews)

    assert len(state_rows) == 3
    assert next(row for row in state_rows if row.condition_label == "DIRECTIONAL_DISPLACEMENT").high_sensitivity_profile_count == 1
    assert next(row for row in window_rows if row.forward_window == 3).profile_count == 2
