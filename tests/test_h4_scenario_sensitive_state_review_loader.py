from pathlib import Path

from sqre.h4_scenario_sensitive_state_review.loader import (
    load_scenario_breakdown,
    load_scenario_comparisons,
    load_scenario_sensitive_profiles,
)


def test_loader_reads_synthetic_h4_scenario_sensitive_inputs(tmp_path: Path):
    dispersion_dir, deep_dive_dir = write_sensitive_inputs(tmp_path)

    profiles = load_scenario_sensitive_profiles(dispersion_dir)
    comparisons = load_scenario_comparisons(deep_dive_dir)
    breakdown = load_scenario_breakdown(deep_dive_dir)

    assert len(profiles) == 5
    assert len(comparisons) == 12
    assert len(breakdown) == 12
    assert profiles[0].condition_label == "DIRECTIONAL_DISPLACEMENT"


def test_loader_handles_case_insensitive_columns(tmp_path: Path):
    dispersion_dir = tmp_path / "dispersion"
    deep_dive_dir = tmp_path / "deep"
    dispersion_dir.mkdir()
    deep_dive_dir.mkdir()
    (dispersion_dir / "h4_scenario_sensitive_profiles.csv").write_text(
        "\n".join(
            [
                "condition_label,forward_window,profile_type,scenario_count,total_sample_size,"
                "forward_range_cv,outcome_magnitude_cv,direction_alignment_dispersion,"
                "high_deviation_scenario_count,dominant_deviation_class,profile_dispersion_class,"
                "profile_research_readiness_class",
                "DIRECTIONAL_EXPANSION,3,RESEARCH_READY,3,90,0.4,0.1,0.05,2,HIGH_DEVIATION,HIGH_DISPERSION,SCENARIO_SENSITIVE_REVIEW",
            ]
        ),
        encoding="utf-8",
    )
    (deep_dive_dir / "h4_state_scenario_comparison_matrix.csv").write_text(
        "\n".join(
            [
                "condition_label,forward_window,scenario_id,sample_size,forward_range_vs_profile_avg,"
                "outcome_magnitude_vs_profile_avg,direction_alignment_vs_profile_avg,scenario_deviation_class",
                "DIRECTIONAL_EXPANSION,3,S1,30,1,0.1,0.01,HIGH_DEVIATION",
            ]
        ),
        encoding="utf-8",
    )
    (deep_dive_dir / "h4_state_scenario_breakdown.csv").write_text(
        "\n".join(
            [
                "condition_label,forward_window,profile_type,scenario_id,timeframe,sample_size",
                "DIRECTIONAL_EXPANSION,3,RESEARCH_READY,S1,H4,30",
            ]
        ),
        encoding="utf-8",
    )

    assert load_scenario_sensitive_profiles(dispersion_dir)[0].forward_range_cv == 0.4
    assert load_scenario_comparisons(deep_dive_dir)[0].scenario_id == "S1"
    assert load_scenario_breakdown(deep_dive_dir)[0].timeframe == "H4"


def write_sensitive_inputs(root: Path) -> tuple[Path, Path]:
    dispersion_dir = root / "dispersion"
    deep_dive_dir = root / "deep"
    dispersion_dir.mkdir(parents=True, exist_ok=True)
    deep_dive_dir.mkdir(parents=True, exist_ok=True)

    (dispersion_dir / "h4_scenario_sensitive_profiles.csv").write_text(
        "\n".join(
            [
                "Condition_Label,Forward_Window,Profile_Type,Scenario_Count,Total_Sample_Size,"
                "Average_Forward_Range_Pips,Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,"
                "Forward_Range_CV,Outcome_Magnitude_CV,Direction_Alignment_Dispersion,"
                "High_Deviation_Scenario_Count,Moderate_Deviation_Scenario_Count,Low_Deviation_Scenario_Count,"
                "Dominant_Deviation_Class,Dispersion_Driver_Class,Profile_Dispersion_Class,"
                "Profile_Research_Readiness_Class,Profile_Dispersion_Diagnostic,Recommended_Follow_Up",
                "DIRECTIONAL_DISPLACEMENT,3,RESEARCH_READY,3,90,15,6,0.5,0.40,0.10,0.05,2,0,1,HIGH_DEVIATION,RANGE_DRIVEN,HIGH_DISPERSION,SCENARIO_SENSITIVE_REVIEW,diag,follow",
                "DIRECTIONAL_EXPANSION,3,RESEARCH_READY,3,90,10,4,0.6,0.18,0.19,0.05,1,1,1,MODERATE_DEVIATION,LOW_DISPERSION,MODERATE_DISPERSION,SCENARIO_SENSITIVE_REVIEW,diag,follow",
                "VOLATILE_ROTATION,6,RESEARCH_READY,3,90,18,7,0.55,0.25,0.22,0.21,0,2,1,MODERATE_DEVIATION,MIXED_DRIVEN,MODERATE_DISPERSION,SCENARIO_SENSITIVE_REVIEW,diag,follow",
                "DIRECTIONAL_DRIFT,12,SAMPLE_CONSTRAINED_OBSERVATION,1,10,8,3,0.4,0.45,0.10,0.05,2,0,1,HIGH_DEVIATION,RANGE_DRIVEN,HIGH_DISPERSION,SAMPLE_REVIEW,diag,follow",
                "OTHER_STATE,3,RESEARCH_READY,3,90,12,5,0.5,0.40,0.10,0.05,2,0,1,HIGH_DEVIATION,RANGE_DRIVEN,HIGH_DISPERSION,SCENARIO_SENSITIVE_REVIEW,diag,follow",
            ]
        ),
        encoding="utf-8",
    )

    comparison_header = (
        "Condition_Label,Forward_Window,Scenario_ID,Sample_Size,Forward_Close_Return_vs_Profile_Avg,"
        "Forward_Range_vs_Profile_Avg,Outcome_Magnitude_vs_Profile_Avg,"
        "Direction_Alignment_vs_Profile_Avg,Scenario_Deviation_Class,Scenario_Comparison_Diagnostic"
    )
    comparison_rows = [
        "DIRECTIONAL_DISPLACEMENT,3,S1,30,1,6,1,0.1,HIGH_DEVIATION,diag",
        "DIRECTIONAL_DISPLACEMENT,3,S2,30,1,7,1,0.1,HIGH_DEVIATION,diag",
        "DIRECTIONAL_DISPLACEMENT,3,S3,30,0,1,0.2,0.01,LOW_DEVIATION,diag",
        "DIRECTIONAL_EXPANSION,3,S1,30,0,2,1,0.1,MODERATE_DEVIATION,diag",
        "DIRECTIONAL_EXPANSION,3,S2,30,0,5,1,0.1,HIGH_DEVIATION,diag",
        "DIRECTIONAL_EXPANSION,3,S3,30,0,1,0.2,0.01,LOW_DEVIATION,diag",
        "VOLATILE_ROTATION,6,S1,30,0,2,2,0.2,MODERATE_DEVIATION,diag",
        "VOLATILE_ROTATION,6,S2,30,0,2,2,0.2,MODERATE_DEVIATION,diag",
        "VOLATILE_ROTATION,6,S3,30,0,1,0.5,0.01,LOW_DEVIATION,diag",
        "DIRECTIONAL_DRIFT,12,S1,10,1,6,1,0.1,HIGH_DEVIATION,diag",
        "DIRECTIONAL_DRIFT,12,S2,0,1,6,1,0.1,HIGH_DEVIATION,diag",
        "OTHER_STATE,3,S1,30,1,6,1,0.1,HIGH_DEVIATION,diag",
    ]
    (deep_dive_dir / "h4_state_scenario_comparison_matrix.csv").write_text(
        "\n".join([comparison_header, *comparison_rows]),
        encoding="utf-8",
    )

    breakdown_header = (
        "Condition_Label,Forward_Window,Profile_Type,Scenario_ID,Timeframe,Sample_Size,"
        "Average_Forward_Close_Return_Pips,Median_Forward_Close_Return_Pips,Average_Forward_Range_Pips,"
        "Average_Favorable_Displacement_Pips,Average_Adverse_Displacement_Pips,"
        "Average_Outcome_Magnitude_Pips,Direction_Alignment_Rate,Sample_Adequacy_Flag,Scenario_Observation_Diagnostic"
    )
    breakdown_rows = []
    for row in comparison_rows:
        condition_label, forward_window, scenario_id, sample_size, *_ = row.split(",")
        breakdown_rows.append(
            ",".join(
                [
                    condition_label,
                    forward_window,
                    "RESEARCH_READY",
                    scenario_id,
                    "H4",
                    sample_size,
                    "1",
                    "1",
                    "10",
                    "5",
                    "3",
                    "4",
                    "0.6",
                    "N",
                    "diag",
                ]
            )
        )
    (deep_dive_dir / "h4_state_scenario_breakdown.csv").write_text(
        "\n".join([breakdown_header, *breakdown_rows]),
        encoding="utf-8",
    )
    return dispersion_dir, deep_dive_dir
