from pathlib import Path

from test_h4_scenario_sensitive_state_review_loader import write_sensitive_inputs
from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig
from sqre.h4_scenario_sensitive_state_review.loader import load_scenario_sensitive_profiles
from sqre.h4_scenario_sensitive_state_review.profile_selector import select_review_profiles


def test_profile_selector_includes_focus_profiles_and_excludes_sample_constrained(tmp_path: Path):
    dispersion_dir, _ = write_sensitive_inputs(tmp_path)

    selected = select_review_profiles(load_scenario_sensitive_profiles(dispersion_dir), H4ScenarioSensitiveStateReviewConfig())

    assert [(row.condition_label, row.forward_window) for row in selected] == [
        ("DIRECTIONAL_DISPLACEMENT", 3),
        ("DIRECTIONAL_EXPANSION", 3),
        ("VOLATILE_ROTATION", 6),
    ]
