from pathlib import Path

from sqre.h4_transition_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
)


def test_loader_reads_synthetic_h4_transition_deep_dive_outputs(tmp_path: Path):
    write_review_inputs(tmp_path)

    profiles = load_profile_inventory(tmp_path)
    statistics = load_outcome_statistics(tmp_path)
    comparisons = load_scenario_comparisons(tmp_path)

    assert len(profiles) == 4
    assert len(statistics) == 4
    assert len(comparisons) == 12
    assert comparisons[0].condition_label == "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT"
    assert comparisons[0].source_state == "DIRECTIONAL_DISPLACEMENT"


def test_loader_handles_case_insensitive_columns(tmp_path: Path):
    (tmp_path / "h4_transition_outcome_statistics.csv").write_text(
        "\n".join(
            [
                "condition_label,source_state,target_state,transition_family,forward_window,profile_type,scenario_count,total_sample_size,"
                "average_sample_size_per_scenario,average_forward_range_pips,"
                "average_outcome_magnitude_pips,average_direction_alignment_rate,"
                "forward_range_cv,outcome_magnitude_cv,direction_alignment_dispersion",
                "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,"
                "DIRECTIONAL_TO_DIRECTIONAL,3,RESEARCH_READY,3,90,30,10,4,0.6,0.1,0.1,0.05",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "h4_transition_scenario_comparison_matrix.csv").write_text(
        "\n".join(
            [
                "condition_label,source_state,target_state,transition_family,forward_window,scenario_id,sample_size,forward_range_vs_profile_avg,"
                "outcome_magnitude_vs_profile_avg,direction_alignment_vs_profile_avg,scenario_deviation_class",
                "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,"
                "DIRECTIONAL_TO_DIRECTIONAL,3,S1,30,1,1,0.1,LOW_DEVIATION",
            ]
        ),
        encoding="utf-8",
    )

    assert load_outcome_statistics(tmp_path)[0].forward_range_cv == 0.1
    assert load_scenario_comparisons(tmp_path)[0].scenario_id == "S1"


def write_review_inputs(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "h4_transition_deep_dive_profile_inventory.csv").write_text(
        "\n".join(
            [
                "Condition_Label,Source_State,Target_State,Transition_Family,Forward_Window,Profile_Type,Scenario_Count,Scenarios_Present,"
                "Total_Sample_Size,Average_Sample_Size_Per_Scenario,Average_Forward_Range_Pips,"
                "Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,Forward_Range_CV,"
                "Outcome_Magnitude_CV,Scenario_Sensitivity_Flag,Sample_Adequacy_Flag,Dispersion_Class,"
                "Transition_Research_Class,Profile_Diagnostic,Recommended_Follow_Up",
                "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,"
                "DIRECTIONAL_TO_DIRECTIONAL,3,RESEARCH_READY,3,S1|S2|S3,90,30,10,4,0.6,0.10,0.10,N,N,STABLE_DESCRIPTIVE,READY,diag,follow",
                "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,"
                "DIRECTIONAL_TO_DIRECTIONAL,3,RESEARCH_READY,3,S1|S2|S3,90,30,15,6,0.5,0.40,0.10,Y,N,HIGH_DISPERSION,READY,diag,follow",
                "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,"
                "DIRECTIONAL_TO_DIRECTIONAL,6,RESEARCH_READY,3,S1|S2|S3,90,30,18,7,0.55,0.25,0.22,N,N,MODERATE_DISPERSION,READY,diag,follow",
                "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT,VOLATILE_ROTATION,DIRECTIONAL_DISPLACEMENT,"
                "ROTATION_TO_DIRECTIONAL,12,SAMPLE_CONSTRAINED_OBSERVATION,1,S1,10,10,8,3,0.4,0.10,0.10,N,Y,STABLE_DESCRIPTIVE,SAMPLE,diag,follow",
            ]
        ),
        encoding="utf-8",
    )
    (root / "h4_transition_outcome_statistics.csv").write_text(
        "\n".join(
            [
                "Condition_Label,Source_State,Target_State,Transition_Family,Forward_Window,Profile_Type,Scenario_Count,Total_Sample_Size,"
                "Average_Sample_Size_Per_Scenario,Average_Forward_Close_Return_Pips,"
                "Min_Forward_Close_Return_Pips,Max_Forward_Close_Return_Pips,"
                "Forward_Close_Return_Dispersion_Pips,Average_Forward_Range_Pips,"
                "Min_Forward_Range_Pips,Max_Forward_Range_Pips,Forward_Range_Dispersion_Pips,"
                "Forward_Range_CV,Average_Outcome_Magnitude_Pips,Min_Outcome_Magnitude_Pips,"
                "Max_Outcome_Magnitude_Pips,Outcome_Magnitude_Dispersion_Pips,Outcome_Magnitude_CV,"
                "Average_Direction_Alignment_Rate,Min_Direction_Alignment_Rate,Max_Direction_Alignment_Rate,"
                "Direction_Alignment_Dispersion,Outcome_Profile_Stability_Class,Outcome_Profile_Diagnostic,Recommended_Follow_Up",
                "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,"
                "DIRECTIONAL_TO_DIRECTIONAL,3,RESEARCH_READY,3,90,30,1,0,2,2,10,9,11,2,0.10,4,3,5,2,0.10,0.6,0.5,0.7,0.2,STABLE_DESCRIPTIVE,diag,follow",
                "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,"
                "DIRECTIONAL_TO_DIRECTIONAL,3,RESEARCH_READY,3,90,30,2,0,4,4,15,10,20,10,0.40,6,4,8,4,0.10,0.5,0.3,0.7,0.4,HIGH_DISPERSION,diag,follow",
                "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,"
                "DIRECTIONAL_TO_DIRECTIONAL,6,RESEARCH_READY,3,90,30,2,1,3,2,18,15,21,6,0.25,7,6,8,2,0.22,0.55,0.5,0.6,0.1,MODERATE_DISPERSION,diag,follow",
                "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT,VOLATILE_ROTATION,DIRECTIONAL_DISPLACEMENT,"
                "ROTATION_TO_DIRECTIONAL,12,SAMPLE_CONSTRAINED_OBSERVATION,1,10,10,1,1,1,0,8,8,8,0,0.10,3,3,3,0,0.10,0.4,0.4,0.4,0.0,STABLE_DESCRIPTIVE,diag,follow",
            ]
        ),
        encoding="utf-8",
    )
    comparison_header = (
        "Condition_Label,Source_State,Target_State,Transition_Family,Forward_Window,Scenario_ID,Sample_Size,Forward_Close_Return_vs_Profile_Avg,"
        "Forward_Range_vs_Profile_Avg,Outcome_Magnitude_vs_Profile_Avg,"
        "Direction_Alignment_vs_Profile_Avg,Scenario_Deviation_Class,Scenario_Comparison_Diagnostic"
    )
    rows = [
        "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_TO_DIRECTIONAL,3,S1,30,0.1,1,0.5,0.01,LOW_DEVIATION,diag",
        "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_TO_DIRECTIONAL,3,S2,30,0.2,2,1.0,0.02,MODERATE_DEVIATION,diag",
        "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_TO_DIRECTIONAL,3,S3,30,0.1,1,0.5,0.01,LOW_DEVIATION,diag",
        "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_TO_DIRECTIONAL,3,S1,30,1.0,6,2.0,0.20,HIGH_DEVIATION,diag",
        "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_TO_DIRECTIONAL,3,S2,30,1.1,7,3.0,0.25,HIGH_DEVIATION,diag",
        "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_TO_DIRECTIONAL,3,S3,30,0.1,1,0.5,0.01,LOW_DEVIATION,diag",
        "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_TO_DIRECTIONAL,6,S1,30,0.1,2,1.0,0.02,MODERATE_DEVIATION,diag",
        "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_TO_DIRECTIONAL,6,S2,30,0.1,2,1.0,0.02,MODERATE_DEVIATION,diag",
        "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_TO_DIRECTIONAL,6,S3,30,0.1,1,0.5,0.01,LOW_DEVIATION,diag",
        "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT,VOLATILE_ROTATION,DIRECTIONAL_DISPLACEMENT,ROTATION_TO_DIRECTIONAL,12,S1,10,0.0,0.0,0.0,0.0,LOW_DEVIATION,diag",
        "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT,VOLATILE_ROTATION,DIRECTIONAL_DISPLACEMENT,ROTATION_TO_DIRECTIONAL,12,S2,0,0.0,0.0,0.0,0.0,LOW_DEVIATION,diag",
        "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT,VOLATILE_ROTATION,DIRECTIONAL_DISPLACEMENT,ROTATION_TO_DIRECTIONAL,12,S3,0,0.0,0.0,0.0,0.0,LOW_DEVIATION,diag",
    ]
    (root / "h4_transition_scenario_comparison_matrix.csv").write_text(
        "\n".join([comparison_header, *rows]),
        encoding="utf-8",
    )
