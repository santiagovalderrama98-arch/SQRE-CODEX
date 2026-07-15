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


def test_loader_supports_real_scenario_summary_aliases(tmp_path: Path):
    scenario_research_dir = tmp_path / "eurusd_h4_period_1" / "research"
    scenario_research_dir.mkdir(parents=True)
    (scenario_research_dir / "condition_price_outcome_summary.csv").write_text(
        "\n".join(
            [
                "Condition_Type,Condition_Value,Forward_Window_Candles,Sample_Size,"
                "Average_Forward_Close_Return_Pips,Median_Forward_Close_Return_Pips,"
                "Average_Forward_Range_Pips,Average_Max_Favorable_Displacement_Pips,"
                "Average_Max_Adverse_Displacement_Pips,Average_Outcome_Magnitude_Pips,"
                "Average_Direction_Alignment_Rate",
                "STATE_CONDITION,DIRECTIONAL_EXPANSION,6,44,1.5,1.0,18.0,13.0,4.0,7.0,0.64",
            ]
        ),
        encoding="utf-8",
    )

    outcomes = load_scenario_outcomes(tmp_path)

    assert len(outcomes) == 1
    assert outcomes[0].condition_label == "DIRECTIONAL_EXPANSION"
    assert outcomes[0].forward_window == 6
    assert outcomes[0].average_favorable_displacement_pips == 13.0
    assert outcomes[0].average_adverse_displacement_pips == 4.0
    assert outcomes[0].direction_alignment_rate == 0.64


def test_loader_fails_when_required_profile_file_is_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_price_outcome_profiles(tmp_path)
