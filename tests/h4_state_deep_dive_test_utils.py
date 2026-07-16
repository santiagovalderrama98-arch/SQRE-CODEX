from pathlib import Path


def write_h4_deep_dive_inputs(research_dir: Path, validation_dir: Path) -> None:
    research_dir.mkdir(parents=True)
    validation_dir.mkdir(parents=True)
    (research_dir / "h4_d1_price_outcome_profiles.csv").write_text(
        "\n".join(
            [
                "Timeframe,Condition_Type,Condition_Label,Forward_Window,Scenario_Count,Scenarios_Present,"
                "Total_Sample_Size,Average_Sample_Size_Per_Scenario,Average_Forward_Close_Return_Pips,"
                "Median_Forward_Close_Return_Pips,Average_Forward_Range_Pips,"
                "Average_Favorable_Displacement_Pips,Average_Adverse_Displacement_Pips,"
                "Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,Forward_Range_CV,"
                "Outcome_Magnitude_CV,Scenario_Sensitivity_Flag,Sample_Adequacy_Flag,Outcome_Profile_Diagnostic",
                "H4,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,2,S1|S2,70,35,2,2,15,12,3,6,0.6,0.10,0.10,N,N,Ready",
                "H4,STATE_CONDITION,DIRECTIONAL_DISPLACEMENT,3,2,S1|S2,70,35,3,3,15,12,3,6,0.6,0.40,0.10,Y,N,Sensitive",
                "H4,STATE_CONDITION,VOLATILE_ROTATION,6,1,S1,12,12,1,1,8,6,2,3,0.4,0.10,0.10,N,Y,Sample",
                "D1,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,2,S1|S2,70,35,2,2,15,12,3,6,0.6,0.10,0.10,N,N,Ignore",
                "H4,TRANSITION_CONDITION,A_TO_B,3,2,S1|S2,70,35,2,2,15,12,3,6,0.6,0.10,0.10,N,N,Ignore",
            ]
        ),
        encoding="utf-8",
    )
    for scenario_id, close_return, range_value, magnitude, alignment in [
        ("eurusd_h4_period_1", 1.0, 10.0, 4.0, 0.5),
        ("eurusd_h4_period_2", 3.0, 20.0, 8.0, 0.7),
    ]:
        scenario_research_dir = validation_dir / scenario_id / "research"
        scenario_research_dir.mkdir(parents=True)
        (scenario_research_dir / "condition_price_outcome_summary.csv").write_text(
            "\n".join(
                [
                    "Timeframe,Condition_Type,Condition_Label,Forward_Window,Sample_Size,"
                    "Average_Forward_Close_Return_Pips,Median_Forward_Close_Return_Pips,"
                    "Average_Forward_Range_Pips,Average_Favorable_Displacement_Pips,"
                    "Average_Adverse_Displacement_Pips,Average_Outcome_Magnitude_Pips,"
                    "Direction_Alignment_Rate,Sample_Adequacy_Flag",
                    f"H4,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,35,{close_return},{close_return},"
                    f"{range_value},8,2,{magnitude},{alignment},ADEQUATE",
                    f"H4,STATE_CONDITION,DIRECTIONAL_DISPLACEMENT,3,35,{close_return + 1},{close_return + 1},"
                    f"{range_value + 2},9,2,{magnitude + 1},{alignment},ADEQUATE",
                    f"H4,STATE_CONDITION,VOLATILE_ROTATION,6,6,{close_return},{close_return},"
                    f"{range_value},6,2,{magnitude},{alignment},LOW",
                ]
            ),
            encoding="utf-8",
        )
