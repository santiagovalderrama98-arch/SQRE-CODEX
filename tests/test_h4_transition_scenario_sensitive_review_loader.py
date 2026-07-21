from pathlib import Path

import pandas as pd

from sqre.h4_transition_scenario_sensitive_review.loader import (
    load_scenario_breakdown,
    load_scenario_comparisons,
    load_scenario_sensitive_profiles,
)


def write_transition_sensitive_inputs(tmp_path: Path) -> tuple[Path, Path]:
    dispersion_dir = tmp_path / "dispersion"
    deep_dive_dir = tmp_path / "deep_dive"
    dispersion_dir.mkdir()
    deep_dive_dir.mkdir()

    profiles = pd.DataFrame(
        [
            {
                "Condition_Label": "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION",
                "Source_State": "DIRECTIONAL_DISPLACEMENT",
                "Target_State": "DIRECTIONAL_EXPANSION",
                "Transition_Family": "DIRECTIONAL_TO_DIRECTIONAL",
                "Forward_Window": 3,
                "Profile_Type": "SCENARIO_SENSITIVE_OBSERVATION",
                "Scenario_Count": 3,
                "Total_Sample_Size": 40,
                "Average_Forward_Range_Pips": 22.0,
                "Average_Outcome_Magnitude_Pips": 18.0,
                "Average_Direction_Alignment_Rate": 0.62,
                "Forward_Range_CV": 0.42,
                "Outcome_Magnitude_CV": 0.41,
                "Direction_Alignment_Dispersion": 0.12,
                "High_Deviation_Scenario_Count": 2,
                "Moderate_Deviation_Scenario_Count": 1,
                "Low_Deviation_Scenario_Count": 0,
                "Dominant_Deviation_Class": "HIGH_DEVIATION",
                "Dispersion_Driver_Class": "MIXED_DRIVEN",
                "Profile_Dispersion_Class": "HIGH_DISPERSION",
                "Transition_Profile_Readiness_Class": "SCENARIO_SENSITIVE_REVIEW",
                "Profile_Dispersion_Diagnostic": "review",
                "Recommended_Follow_Up": "review",
            },
            {
                "Condition_Label": "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT",
                "Source_State": "DIRECTIONAL_DISPLACEMENT",
                "Target_State": "DIRECTIONAL_DISPLACEMENT",
                "Transition_Family": "DIRECTIONAL_TO_DIRECTIONAL",
                "Forward_Window": 6,
                "Profile_Type": "SCENARIO_SENSITIVE_OBSERVATION",
                "Scenario_Count": 3,
                "Total_Sample_Size": 90,
                "Average_Forward_Range_Pips": 20.0,
                "Average_Outcome_Magnitude_Pips": 12.0,
                "Average_Direction_Alignment_Rate": 0.54,
                "Forward_Range_CV": 0.21,
                "Outcome_Magnitude_CV": 0.11,
                "Direction_Alignment_Dispersion": 0.08,
                "High_Deviation_Scenario_Count": 1,
                "Moderate_Deviation_Scenario_Count": 2,
                "Low_Deviation_Scenario_Count": 0,
                "Dominant_Deviation_Class": "MODERATE_DEVIATION",
                "Dispersion_Driver_Class": "RANGE_DRIVEN",
                "Profile_Dispersion_Class": "MODERATE_DISPERSION",
                "Transition_Profile_Readiness_Class": "SCENARIO_SENSITIVE_REVIEW",
                "Profile_Dispersion_Diagnostic": "review",
                "Recommended_Follow_Up": "review",
            },
            {
                "Condition_Label": "BALANCED_ROTATION -> VOLATILE_ROTATION",
                "Source_State": "BALANCED_ROTATION",
                "Target_State": "VOLATILE_ROTATION",
                "Transition_Family": "ROTATION_TO_ROTATION",
                "Forward_Window": 3,
                "Profile_Type": "SCENARIO_SENSITIVE_OBSERVATION",
                "Scenario_Count": 3,
                "Total_Sample_Size": 50,
                "Average_Forward_Range_Pips": 16.0,
                "Average_Outcome_Magnitude_Pips": 11.0,
                "Average_Direction_Alignment_Rate": 0.44,
                "Forward_Range_CV": 0.08,
                "Outcome_Magnitude_CV": 0.43,
                "Direction_Alignment_Dispersion": 0.09,
                "High_Deviation_Scenario_Count": 2,
                "Moderate_Deviation_Scenario_Count": 1,
                "Low_Deviation_Scenario_Count": 0,
                "Dominant_Deviation_Class": "HIGH_DEVIATION",
                "Dispersion_Driver_Class": "MAGNITUDE_DRIVEN",
                "Profile_Dispersion_Class": "HIGH_DISPERSION",
                "Transition_Profile_Readiness_Class": "SCENARIO_SENSITIVE_REVIEW",
                "Profile_Dispersion_Diagnostic": "review",
                "Recommended_Follow_Up": "review",
            },
            {
                "Condition_Label": "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT",
                "Source_State": "VOLATILE_ROTATION",
                "Target_State": "DIRECTIONAL_DISPLACEMENT",
                "Transition_Family": "ROTATION_TO_DIRECTIONAL",
                "Forward_Window": 12,
                "Profile_Type": "SAMPLE_CONSTRAINED_OBSERVATION",
                "Scenario_Count": 1,
                "Total_Sample_Size": 5,
                "Average_Forward_Range_Pips": 10.0,
                "Average_Outcome_Magnitude_Pips": 8.0,
                "Average_Direction_Alignment_Rate": 0.40,
                "Forward_Range_CV": 0.5,
                "Outcome_Magnitude_CV": 0.5,
                "Direction_Alignment_Dispersion": 0.5,
                "High_Deviation_Scenario_Count": 1,
                "Moderate_Deviation_Scenario_Count": 0,
                "Low_Deviation_Scenario_Count": 0,
                "Dominant_Deviation_Class": "HIGH_DEVIATION",
                "Dispersion_Driver_Class": "MIXED_DRIVEN",
                "Profile_Dispersion_Class": "HIGH_DISPERSION",
                "Transition_Profile_Readiness_Class": "SAMPLE_REVIEW",
                "Profile_Dispersion_Diagnostic": "sample",
                "Recommended_Follow_Up": "review",
            },
        ]
    )
    profiles.to_csv(dispersion_dir / "h4_transition_scenario_sensitive_profiles.csv", index=False)

    comparison_rows = []
    for condition, source, target, family, window in [
        (
            "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION",
            "DIRECTIONAL_DISPLACEMENT",
            "DIRECTIONAL_EXPANSION",
            "DIRECTIONAL_TO_DIRECTIONAL",
            3,
        ),
        (
            "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT",
            "DIRECTIONAL_DISPLACEMENT",
            "DIRECTIONAL_DISPLACEMENT",
            "DIRECTIONAL_TO_DIRECTIONAL",
            6,
        ),
        (
            "BALANCED_ROTATION -> VOLATILE_ROTATION",
            "BALANCED_ROTATION",
            "VOLATILE_ROTATION",
            "ROTATION_TO_ROTATION",
            3,
        ),
    ]:
        comparison_rows.extend(
            [
                _comparison(condition, source, target, family, window, "S1", 0.30, 0.42, 0.12, "HIGH_DEVIATION"),
                _comparison(condition, source, target, family, window, "S2", 0.10, 0.18, 0.08, "MODERATE_DEVIATION"),
                _comparison(condition, source, target, family, window, "S3", 0.03, 0.02, 0.01, "LOW_DEVIATION"),
            ]
        )
    pd.DataFrame(comparison_rows).to_csv(deep_dive_dir / "h4_transition_scenario_comparison_matrix.csv", index=False)

    breakdown = pd.DataFrame(
        [
            {
                "Condition_Label": row["Condition_Label"],
                "Source_State": row["Source_State"],
                "Target_State": row["Target_State"],
                "Transition_Family": row["Transition_Family"],
                "Forward_Window": row["Forward_Window"],
                "Profile_Type": "SCENARIO_SENSITIVE_OBSERVATION",
                "Scenario_ID": "S1",
                "Timeframe": "H4",
                "Sample_Size": 12,
                "Average_Forward_Close_Return_Pips": 1.0,
                "Median_Forward_Close_Return_Pips": 0.5,
                "Average_Forward_Range_Pips": 20.0,
                "Average_Favorable_Displacement_Pips": 15.0,
                "Average_Adverse_Displacement_Pips": 10.0,
                "Average_Outcome_Magnitude_Pips": 12.0,
                "Direction_Alignment_Rate": 0.5,
                "Sample_Adequacy_Flag": "ADEQUATE",
                "Scenario_Observation_Diagnostic": "synthetic",
            }
            for row in comparison_rows
        ]
    )
    breakdown.to_csv(deep_dive_dir / "h4_transition_scenario_breakdown.csv", index=False)
    return dispersion_dir, deep_dive_dir


def test_loader_reads_transition_inputs(tmp_path: Path):
    dispersion_dir, deep_dive_dir = write_transition_sensitive_inputs(tmp_path)

    profiles = load_scenario_sensitive_profiles(dispersion_dir)
    comparisons = load_scenario_comparisons(deep_dive_dir)
    breakdown = load_scenario_breakdown(deep_dive_dir)

    assert len(profiles) == 4
    assert profiles[0].source_state == "DIRECTIONAL_DISPLACEMENT"
    assert len(comparisons) == 9
    assert len(breakdown) == 9


def test_loader_handles_case_insensitive_profile_columns(tmp_path: Path):
    dispersion_dir, _ = write_transition_sensitive_inputs(tmp_path)
    frame = pd.read_csv(dispersion_dir / "h4_transition_scenario_sensitive_profiles.csv")
    frame.columns = [column.lower() for column in frame.columns]
    frame.to_csv(dispersion_dir / "h4_transition_scenario_sensitive_profiles.csv", index=False)

    profiles = load_scenario_sensitive_profiles(dispersion_dir)

    assert profiles[0].condition_label == "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION"
    assert profiles[0].transition_profile_readiness_class == "SCENARIO_SENSITIVE_REVIEW"


def _comparison(
    condition: str,
    source: str,
    target: str,
    family: str,
    window: int,
    scenario: str,
    range_value: float,
    magnitude: float,
    alignment: float,
    deviation_class: str,
) -> dict[str, object]:
    return {
        "Condition_Label": condition,
        "Source_State": source,
        "Target_State": target,
        "Transition_Family": family,
        "Forward_Window": window,
        "Scenario_ID": scenario,
        "Sample_Size": 15,
        "Forward_Close_Return_vs_Profile_Avg": 0.0,
        "Forward_Range_vs_Profile_Avg": range_value,
        "Outcome_Magnitude_vs_Profile_Avg": magnitude,
        "Direction_Alignment_vs_Profile_Avg": alignment,
        "Scenario_Deviation_Class": deviation_class,
        "Scenario_Comparison_Diagnostic": "synthetic",
    }
