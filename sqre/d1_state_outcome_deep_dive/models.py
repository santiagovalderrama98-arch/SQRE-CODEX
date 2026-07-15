"""Models for D1 state outcome deep dive."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_PROFILE_COLUMNS = [
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
]

REQUIRED_OUTCOME_COLUMNS = [
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Regime_ID",
    "Regime_Label",
    "Scenario_ID",
    "Sample_Size",
    "Average_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
]


@dataclass(frozen=True)
class StateProfile:
    condition_type: str
    condition_label: str
    forward_window: int
    profile_type: str
    regime_count: int = 0
    regimes_present: str = ""
    scenario_count: int = 0
    total_sample_size: int = 0
    average_sample_size_per_regime: float = 0.0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    average_direction_alignment_rate: float = 0.0
    forward_range_cv: float = 0.0
    outcome_magnitude_cv: float = 0.0
    direction_alignment_cv: float = 0.0
    sample_adequacy_class: str = ""
    regime_coverage_class: str = ""
    dispersion_class: str = ""
    sensitivity_class: str = ""
    condition_research_class: str = ""
    profile_diagnostic: str = ""
    recommended_follow_up: str = ""


@dataclass(frozen=True)
class RegimeOutcome:
    condition_type: str
    condition_label: str
    forward_window: int
    regime_id: str
    regime_label: str
    scenario_id: str
    timeframe: str = ""
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
class RegimeBreakdownRow:
    condition_label: str
    forward_window: int
    profile_type: str
    regime_id: str
    regime_label: str
    scenario_id: str
    sample_size: int
    average_forward_close_return_pips: float
    median_forward_close_return_pips: float
    average_forward_range_pips: float
    average_favorable_displacement_pips: float
    average_adverse_displacement_pips: float
    average_outcome_magnitude_pips: float
    direction_alignment_rate: float
    sample_adequacy_flag: str
    regime_observation_diagnostic: str


@dataclass(frozen=True)
class OutcomeStatisticsRow:
    condition_label: str
    forward_window: int
    profile_type: str
    regime_count: int
    total_sample_size: int
    average_sample_size_per_regime: float
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
class RegimeComparisonRow:
    condition_label: str
    forward_window: int
    regime_id: str
    regime_label: str
    scenario_id: str
    sample_size: int
    forward_close_return_vs_profile_avg: float
    forward_range_vs_profile_avg: float
    outcome_magnitude_vs_profile_avg: float
    direction_alignment_vs_profile_avg: float
    regime_deviation_class: str
    regime_comparison_diagnostic: str


@dataclass(frozen=True)
class StateDeepDiveSummaryRow:
    condition_label: str
    profile_count: int
    research_ready_profile_count: int
    regime_sensitive_observation_count: int
    total_sample_size: int
    average_regime_count: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    stable_profile_count: int
    moderate_profile_count: int
    high_dispersion_profile_count: int
    state_deep_dive_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class D1StateOutcomeDeepDiveResult:
    outcome_review_dir: Path
    regime_research_dir: Path
    output_dir: Path
    report_path: Path
    research_ready_profiles_loaded: int = 0
    regime_sensitive_profiles_loaded: int = 0
    regime_outcomes_loaded: int = 0
    selected_profiles: list[StateProfile] = field(default_factory=list)
    regime_breakdown_rows: list[RegimeBreakdownRow] = field(default_factory=list)
    outcome_statistics_rows: list[OutcomeStatisticsRow] = field(default_factory=list)
    comparison_rows: list[RegimeComparisonRow] = field(default_factory=list)
    summary_rows: list[StateDeepDiveSummaryRow] = field(default_factory=list)
