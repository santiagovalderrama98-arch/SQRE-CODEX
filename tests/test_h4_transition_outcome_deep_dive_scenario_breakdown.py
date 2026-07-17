from pathlib import Path

from test_h4_transition_outcome_deep_dive_loader import write_transition_inputs
from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.loader import load_price_outcome_profiles, load_scenario_outcomes
from sqre.h4_transition_outcome_deep_dive.profile_selector import select_h4_transition_profiles
from sqre.h4_transition_outcome_deep_dive.scenario_breakdown import build_scenario_breakdown


def test_scenario_breakdown_joins_selected_profiles_to_scenario_outcomes(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    config = H4TransitionOutcomeDeepDiveConfig()
    write_transition_inputs(research_dir, validation_dir)

    selected = select_h4_transition_profiles(load_price_outcome_profiles(research_dir), config)
    rows = build_scenario_breakdown(selected, load_scenario_outcomes(validation_dir), config)

    assert len(rows) == 6
    assert rows[0].transition_family
    assert rows[0].scenario_observation_diagnostic
