from pathlib import Path

from test_h4_transition_outcome_deep_dive_loader import write_transition_inputs
from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.loader import load_price_outcome_profiles
from sqre.h4_transition_outcome_deep_dive.profile_selector import select_h4_transition_profiles


def test_profile_selector_filters_and_classifies_h4_transition_profiles(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    write_transition_inputs(research_dir, validation_dir)

    selected = select_h4_transition_profiles(load_price_outcome_profiles(research_dir), H4TransitionOutcomeDeepDiveConfig())

    assert len(selected) == 3
    assert {row.profile_type for row in selected} == {
        "RESEARCH_READY",
        "SCENARIO_SENSITIVE_OBSERVATION",
        "SAMPLE_CONSTRAINED_OBSERVATION",
    }
    assert all(row.condition_label != "DIRECTIONAL_EXPANSION" for row in selected)
    assert selected[0].source_state != "UNKNOWN"
