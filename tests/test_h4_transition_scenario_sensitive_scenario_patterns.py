from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    build_scenario_deviation_details,
)
from sqre.h4_transition_scenario_sensitive_review.loader import (
    load_scenario_comparisons,
    load_scenario_sensitive_profiles,
)
from sqre.h4_transition_scenario_sensitive_review.profile_selector import select_review_profiles
from sqre.h4_transition_scenario_sensitive_review.scenario_patterns import build_scenario_recurrent_deviation_summary


def test_scenario_recurrent_deviation_summary(tmp_path: Path):
    dispersion_dir, deep_dive_dir = write_transition_sensitive_inputs(tmp_path)
    config = H4TransitionScenarioSensitiveReviewConfig()
    selected = select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), config)
    details = build_scenario_deviation_details(selected, load_scenario_comparisons(deep_dive_dir), config)

    summaries = build_scenario_recurrent_deviation_summary(details)

    assert len(summaries) == 3
    s1 = next(row for row in summaries if row.scenario_id == "S1")
    assert s1.scenario_profile_count == 3
    assert s1.scenario_recurrent_deviation_class == "HIGH_RECURRENT_DEVIATION"
