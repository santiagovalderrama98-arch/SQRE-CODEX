from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.loader import load_scenario_sensitive_profiles
from sqre.h4_transition_scenario_sensitive_review.profile_selector import focus_transition_flag, select_review_profiles


def test_profile_selector_includes_only_scenario_sensitive_transition_profiles(tmp_path: Path):
    dispersion_dir, _ = write_transition_sensitive_inputs(tmp_path)
    profiles = load_scenario_sensitive_profiles(dispersion_dir)

    selected = select_review_profiles(profiles, H4TransitionScenarioSensitiveReviewConfig())

    assert len(selected) == 3
    assert all(row.profile_type != "SAMPLE_CONSTRAINED_OBSERVATION" for row in selected)


def test_focus_transition_flag_marks_configured_transitions():
    config = H4TransitionScenarioSensitiveReviewConfig()

    assert focus_transition_flag("DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION", config) == "YES"
    assert focus_transition_flag("BALANCED_ROTATION -> VOLATILE_ROTATION", config) == "NO"
