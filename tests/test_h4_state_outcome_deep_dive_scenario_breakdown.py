from pathlib import Path

from h4_state_deep_dive_test_utils import write_h4_deep_dive_inputs
from sqre.h4_state_outcome_deep_dive.config import H4StateOutcomeDeepDiveConfig
from sqre.h4_state_outcome_deep_dive.loader import load_price_outcome_profiles, load_scenario_outcomes
from sqre.h4_state_outcome_deep_dive.profile_selector import select_h4_state_profiles
from sqre.h4_state_outcome_deep_dive.scenario_breakdown import build_scenario_breakdown


def test_scenario_breakdown_matches_selected_h4_state_profiles(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    write_h4_deep_dive_inputs(research_dir, validation_dir)
    config = H4StateOutcomeDeepDiveConfig()

    selected = select_h4_state_profiles(load_price_outcome_profiles(research_dir), config)
    rows = build_scenario_breakdown(selected, load_scenario_outcomes(validation_dir), config)

    assert len(rows) == 6
    assert rows[0].scenario_id == "eurusd_h4_period_1"
    assert "Scenario observation" in rows[0].scenario_observation_diagnostic
