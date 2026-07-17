"""Models for H4 transition outcome deep dive."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_PROFILE_COLUMNS = [
    "Timeframe",
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Scenario_Count",
    "Total_Sample_Size",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
]

REQUIRED_SCENARIO_OUTCOME_COLUMNS = [
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Sample_Size",
    "Average_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
]


@dataclass(frozen=True)
class TransitionParseResult:
    source_state: str
    target_state: str
    transition_family: str


@dataclass(frozen=True)
class H4TransitionProfileInput:
    timeframe: str
    condition_type: str
    condition_label: str
    forward_window: int
    scenario_count: int
    scenarios_present: str = ""
    total_sample_size: int = 0
    average_sample_size_per_scenario: float = 0.0
    average_forward_close_return_pips: float = 0.0
    median_forward_close_return_pips: float = 0.0
    average_forward_range_pips: float = 0.0
    average_favorable_displacement_pips: float = 0.0
    average_adverse_displacement_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    average_direction_alignment_rate: float = 0.0
    forward_range_cv: float = 0.0
    outcome_magnitude_cv: float = 0.0
    scenario_sensitivity_flag: str = ""
    sample_adequacy_flag: str = ""
    outcome_profile_diagnostic: str = ""


@dataclass(frozen=True)
class H4TransitionProfile:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    profile_type: str
    scenario_count: int
    scenarios_present: str
    total_sample_size: int
    average_sample_size_per_scenario: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    forward_range_cv: float
    outcome_magnitude_cv: float
    scenario_sensitivity_flag: str
    sample_adequacy_flag: str
    dispersion_class: str
    transition_research_class: str
    profile_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ScenarioOutcome:
    scenario_id: str
    timeframe: str
    condition_type: str
    condition_label: str
    forward_window: int
    sample_size: int = 0
    average_forward_close_return_pips: float = 0.0
    median_forward_close_return_pips: float = 0.0
    average_forward_range_pips: float = 0.0
    average_favorable_displacement_pips: float = 0.0
    average_adverse_displacement_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    direction_alignment_rate: float = 0.0
    sample_adequacy_flag: str = ""


@dataclass(frozen=True)
class ScenarioBreakdownRow:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    profile_type: str
    scenario_id: str
    timeframe: str
    sample_size: int
    average_forward_close_return_pips: float
    median_forward_close_return_pips: float
    average_forward_range_pips: float
    average_favorable_displacement_pips: float
    average_adverse_displacement_pips: float
    average_outcome_magnitude_pips: float
    direction_alignment_rate: float
    sample_adequacy_flag: str
    scenario_observation_diagnostic: str


@dataclass(frozen=True)
class OutcomeStatisticsRow:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    profile_type: str
    scenario_count: int
    total_sample_size: int
    average_sample_size_per_scenario: float
    average_forward_close_return_pips: float
    min_forward_close_return_pips: float
    max_forward_close_return_pips: float
    forward_close_return_dispersion_pips: float
    average_forward_range_pips: float
    min_forward_range_pips: float
    max_forward_range_pips: float
    forward_range_dispersion_pips: float
    forward_range_cv: float
    average_outcome_magnitude_pips: float
    min_outcome_magnitude_pips: float
    max_outcome_magnitude_pips: float
    outcome_magnitude_dispersion_pips: float
    outcome_magnitude_cv: float
    average_direction_alignment_rate: float
    min_direction_alignment_rate: float
    max_direction_alignment_rate: float
    direction_alignment_dispersion: float
    outcome_profile_stability_class: str
    outcome_profile_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ScenarioComparisonRow:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    scenario_id: str
    sample_size: int
    forward_close_return_vs_profile_avg: float
    forward_range_vs_profile_avg: float
    outcome_magnitude_vs_profile_avg: float
    direction_alignment_vs_profile_avg: float
    scenario_deviation_class: str
    scenario_comparison_diagnostic: str


@dataclass(frozen=True)
class TransitionSummaryRow:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    profile_count: int
    research_ready_profile_count: int
    scenario_sensitive_observation_count: int
    sample_constrained_observation_count: int
    total_sample_size: int
    average_scenario_count: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    stable_profile_count: int
    moderate_profile_count: int
    high_dispersion_profile_count: int
    transition_deep_dive_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class TransitionFamilySummaryRow:
    transition_family: str
    profile_count: int
    research_ready_profile_count: int
    scenario_sensitive_observation_count: int
    sample_constrained_observation_count: int
    total_sample_size: int
    average_scenario_count: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    stable_profile_count: int
    moderate_profile_count: int
    high_dispersion_profile_count: int
    transition_family_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TransitionOutcomeDeepDiveResult:
    h4_d1_research_dir: Path
    validation_output_dir: Path
    output_dir: Path
    report_path: Path
    price_profiles_loaded: int = 0
    scenario_outcomes_loaded: int = 0
    selected_profiles: list[H4TransitionProfile] = field(default_factory=list)
    scenario_breakdown_rows: list[ScenarioBreakdownRow] = field(default_factory=list)
    outcome_statistics_rows: list[OutcomeStatisticsRow] = field(default_factory=list)
    comparison_rows: list[ScenarioComparisonRow] = field(default_factory=list)
    family_summary_rows: list[TransitionFamilySummaryRow] = field(default_factory=list)
    summary_rows: list[TransitionSummaryRow] = field(default_factory=list)
