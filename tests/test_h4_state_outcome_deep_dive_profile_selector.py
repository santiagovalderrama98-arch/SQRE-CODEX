from pathlib import Path

from h4_state_deep_dive_test_utils import write_h4_deep_dive_inputs
from sqre.h4_state_outcome_deep_dive.config import H4StateOutcomeDeepDiveConfig
from sqre.h4_state_outcome_deep_dive.loader import load_price_outcome_profiles
from sqre.h4_state_outcome_deep_dive.profile_selector import select_h4_state_profiles


def test_selector_keeps_only_h4_state_conditions_and_classifies_profiles(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    write_h4_deep_dive_inputs(research_dir, validation_dir)

    selected = select_h4_state_profiles(load_price_outcome_profiles(research_dir), H4StateOutcomeDeepDiveConfig())

    assert [profile.profile_type for profile in selected] == [
        "SCENARIO_SENSITIVE_OBSERVATION",
        "RESEARCH_READY",
        "SAMPLE_CONSTRAINED_OBSERVATION",
    ]


def test_selector_can_exclude_sample_constrained_observations(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    write_h4_deep_dive_inputs(research_dir, validation_dir)
    config = H4StateOutcomeDeepDiveConfig(include_sample_constrained_observations=False)

    selected = select_h4_state_profiles(load_price_outcome_profiles(research_dir), config)

    assert {profile.profile_type for profile in selected} == {"RESEARCH_READY", "SCENARIO_SENSITIVE_OBSERVATION"}
