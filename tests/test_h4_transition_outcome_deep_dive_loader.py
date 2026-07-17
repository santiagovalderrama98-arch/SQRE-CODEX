from pathlib import Path

import pytest

from sqre.h4_transition_outcome_deep_dive.loader import load_price_outcome_profiles, load_scenario_outcomes


def write_transition_inputs(research_dir: Path, validation_dir: Path) -> None:
    research_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "h4_d1_price_outcome_profiles.csv").write_text(
        "\n".join(
            [
                "Timeframe,Condition_Type,Condition_Label,Forward_Window,Scenario_Count,Scenarios_Present,"
                "Total_Sample_Size,Average_Sample_Size_Per_Scenario,Average_Forward_Close_Return_Pips,"
                "Median_Forward_Close_Return_Pips,Average_Forward_Range_Pips,"
                "Average_Favorable_Displacement_Pips,Average_Adverse_Displacement_Pips,"
                "Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,Forward_Range_CV,"
                "Outcome_Magnitude_CV,Scenario_Sensitivity_Flag,Sample_Adequacy_Flag,Outcome_Profile_Diagnostic",
                "H4,TRANSITION_CONDITION,DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,3,2,S1|S2,70,35,2,2,15,12,3,6,0.6,0.10,0.10,N,N,Ready",
                "H4,TRANSITION_CONDITION,DIRECTIONAL_EXPANSION_TO_DIRECTIONAL_DISPLACEMENT,6,2,S1|S2,80,40,3,3,18,14,4,7,0.7,0.40,0.10,Y,N,Sensitive",
                "H4,TRANSITION_CONDITION,VOLATILE_ROTATION|DIRECTIONAL_DISPLACEMENT,12,1,S1,12,12,1,1,8,6,2,3,0.4,0.10,0.10,N,Y,Sample",
                "H4,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,2,S1|S2,70,35,2,2,15,12,3,6,0.6,0.10,0.10,N,N,Ignore",
                "D1,TRANSITION_CONDITION,DIRECTIONAL_EXPANSION -> DIRECTIONAL_EXPANSION,3,2,S1|S2,70,35,2,2,15,12,3,6,0.6,0.10,0.10,N,N,Ignore",
            ]
        ),
        encoding="utf-8",
    )
    for scenario_id, close_return, range_value, magnitude, alignment in [
        ("eurusd_h4_period_1", 1.0, 10.0, 4.0, 0.5),
        ("eurusd_h4_period_2", 3.0, 20.0, 8.0, 0.7),
    ]:
        scenario_research_dir = validation_dir / scenario_id / "research"
        scenario_research_dir.mkdir(parents=True, exist_ok=True)
        (scenario_research_dir / "condition_price_outcome_summary.csv").write_text(
            "\n".join(
                [
                    "Timeframe,Condition_Type,Condition_Value,Forward_Window_Candles,Sample_Size,"
                    "Average_Forward_Close_Return_Pips,Median_Forward_Close_Return_Pips,"
                    "Average_Forward_Range_Pips,Average_Max_Favorable_Displacement_Pips,"
                    "Average_Max_Adverse_Displacement_Pips,Average_Outcome_Magnitude_Pips,"
                    "Average_Direction_Alignment_Rate,Sample_Adequacy_Flag",
                    f"H4,TRANSITION_CONDITION,DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,3,35,{close_return},{close_return},"
                    f"{range_value},8,2,{magnitude},{alignment},ADEQUATE",
                    f"H4,TRANSITION_CONDITION,DIRECTIONAL_EXPANSION_TO_DIRECTIONAL_DISPLACEMENT,6,40,{close_return + 1},{close_return + 1},"
                    f"{range_value + 2},9,2,{magnitude + 1},{alignment},ADEQUATE",
                    f"H4,TRANSITION_CONDITION,VOLATILE_ROTATION|DIRECTIONAL_DISPLACEMENT,12,6,{close_return},{close_return},"
                    f"{range_value},6,2,{magnitude},{alignment},LOW",
                ]
            ),
            encoding="utf-8",
        )


def test_loader_reads_price_profiles_and_scenario_outcomes(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    write_transition_inputs(research_dir, validation_dir)

    profiles = load_price_outcome_profiles(research_dir)
    outcomes = load_scenario_outcomes(validation_dir)

    assert len(profiles) == 5
    assert len(outcomes) == 6
    assert outcomes[0].condition_label == "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION"
    assert outcomes[0].forward_window == 3
    assert outcomes[0].average_favorable_displacement_pips == 8.0


def test_loader_fails_when_required_profile_file_is_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_price_outcome_profiles(tmp_path)
