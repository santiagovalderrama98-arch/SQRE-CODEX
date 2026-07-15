from pathlib import Path

import pytest

from h4_state_deep_dive_test_utils import write_h4_deep_dive_inputs
from sqre.h4_state_outcome_deep_dive.loader import load_price_outcome_profiles, load_scenario_outcomes


def test_loader_reads_price_profiles_case_insensitively(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    write_h4_deep_dive_inputs(research_dir, validation_dir)

    profiles = load_price_outcome_profiles(research_dir)

    assert len(profiles) == 5
    assert profiles[0].condition_label == "DIRECTIONAL_EXPANSION"
    assert profiles[0].scenario_count == 2


def test_loader_reads_scenario_outcomes_from_nested_research_dirs(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    write_h4_deep_dive_inputs(research_dir, validation_dir)

    outcomes = load_scenario_outcomes(validation_dir)

    assert len(outcomes) == 6
    assert outcomes[0].scenario_id == "eurusd_h4_period_1"
    assert outcomes[0].timeframe == "H4"


def test_loader_fails_when_required_profile_file_is_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_price_outcome_profiles(tmp_path)
