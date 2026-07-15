"""Models for M15 duration calibration review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_COLUMNS = [
    "Scenario_ID",
    "Timeframe",
    "Experiment_Profile",
    "Status",
    "Max_Structure_Duration_Seconds",
    "Structures_Detected",
    "Average_Structure_Duration",
    "Unique_States",
    "Most_Common_State",
    "Average_Forward_Range_Pips",
    "Direction_Alignment_Rate",
    "Low_Sample_Conditions_Research",
    "Low_Sample_Conditions_Price_Outcome",
]


OPTIONAL_COUNT_COLUMNS = [
    "States_Generated",
    "Directional_Displacement_Count",
    "Directional_Expansion_Count",
    "Directional_Drift_Count",
    "Volatile_Rotation_Count",
    "Complex_Consolidation_Count",
    "Low_Quality_Structure_Count",
    "Unclassified_Count",
    "Average_Outcome_Magnitude_Pips",
]


OPTIONAL_RATIO_COLUMNS = [
    "Directional_State_Ratio",
    "Complex_Consolidation_Ratio",
    "Volatile_Rotation_Ratio",
    "Low_Quality_Rate",
    "Unclassified_Rate",
]


@dataclass(frozen=True)
class M15DurationExperimentRunRow:
    scenario_id: str
    timeframe: str
    experiment_profile: str
    status: str
    max_structure_duration_seconds: int
    structures_detected: int
    average_structure_duration: float
    unique_states: int
    most_common_state: str
    average_forward_range_pips: float
    direction_alignment_rate: float
    low_sample_conditions_research: int
    low_sample_conditions_price_outcome: int
    states_generated: int = 0
    directional_displacement_count: int = 0
    directional_expansion_count: int = 0
    directional_drift_count: int = 0
    volatile_rotation_count: int = 0
    complex_consolidation_count: int = 0
    low_quality_structure_count: int = 0
    unclassified_count: int = 0
    average_outcome_magnitude_pips: float = 0.0
    directional_state_ratio: float | None = None
    complex_consolidation_ratio: float | None = None
    volatile_rotation_ratio: float | None = None
    low_quality_rate: float | None = None
    unclassified_rate: float | None = None
    has_directional_count_columns: bool = True
    has_complex_consolidation_count_column: bool = True
    has_volatile_rotation_count_column: bool = True
    has_low_quality_count_column: bool = True
    has_unclassified_count_column: bool = True


@dataclass(frozen=True)
class M15DurationReviewRow:
    timeframe: str
    experiment_profile: str
    scenario_count: int
    completed_run_count: int
    failed_run_count: int
    missing_input_count: int
    scenario_ids: str
    max_structure_duration_seconds: int
    average_structures_detected: float
    min_structures_detected: int
    max_structures_detected: int
    structure_count_range: int
    structure_count_cv: float
    average_structure_duration: float
    average_duration_utilization_ratio: float
    min_duration_utilization_ratio: float
    max_duration_utilization_ratio: float
    average_unique_states: float
    min_unique_states: int
    max_unique_states: int
    state_diversity_range: int
    most_common_state_mode: str
    directional_displacement_total: int
    directional_expansion_total: int
    directional_drift_total: int
    volatile_rotation_total: int
    complex_consolidation_total: int
    low_quality_structure_total: int
    unclassified_total: int
    average_directional_state_ratio: float
    average_complex_consolidation_ratio: float
    average_volatile_rotation_ratio: float
    average_low_quality_rate: float
    average_unclassified_rate: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    average_low_sample_conditions_research: float
    average_low_sample_conditions_price_outcome: float
    max_low_sample_conditions_research: int
    max_low_sample_conditions_price_outcome: int
    baseline_profile: str
    baseline_structures_detected: float | None
    relative_structure_change_vs_baseline: float | None
    relative_duration_utilization_change_vs_baseline: float | None
    relative_unique_states_change_vs_baseline: float | None
    relative_low_sample_research_change_vs_baseline: float | None
    relative_low_sample_price_outcome_change_vs_baseline: float | None
    relative_forward_range_change_vs_baseline: float | None
    relative_direction_alignment_change_vs_baseline: float | None
    structure_stability_flag: str
    duration_utilization_flag: str
    state_diversity_flag: str
    low_sample_pressure_flag: str
    fragmentation_flag: str
    compression_flag: str
    profile_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class M15DurationReviewFinding:
    timeframe: str
    experiment_profile: str
    finding_type: str
    flag: str
    message: str


@dataclass(frozen=True)
class M15DurationReviewResult:
    input_experiment_summary: str
    rows_loaded: int
    profiles_reviewed: int
    output_path: Path
    report_path: Path
    rows: list[M15DurationReviewRow] = field(default_factory=list)
