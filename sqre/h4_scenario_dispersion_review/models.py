"""Models for H4 scenario dispersion review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProfileInventoryRow:
    condition_label: str
    forward_window: int
    profile_type: str
    scenario_count: int = 0
    scenarios_present: str = ""
    total_sample_size: int = 0
    average_sample_size_per_scenario: float = 0.0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    average_direction_alignment_rate: float = 0.0
    forward_range_cv: float = 0.0
    outcome_magnitude_cv: float = 0.0
    scenario_sensitivity_flag: str = ""
    sample_adequacy_flag: str = ""
    dispersion_class: str = ""
    condition_research_class: str = ""
    profile_diagnostic: str = ""
    recommended_follow_up: str = ""


@dataclass(frozen=True)
class OutcomeStatisticsInput:
    condition_label: str
    forward_window: int
    profile_type: str
    scenario_count: int = 0
    total_sample_size: int = 0
    average_sample_size_per_scenario: float = 0.0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    average_direction_alignment_rate: float = 0.0
    forward_range_cv: float = 0.0
    outcome_magnitude_cv: float = 0.0
    direction_alignment_dispersion: float = 0.0


@dataclass(frozen=True)
class ScenarioComparisonInput:
    condition_label: str
    forward_window: int
    scenario_id: str
    sample_size: int = 0
    forward_range_vs_profile_avg: float = 0.0
    outcome_magnitude_vs_profile_avg: float = 0.0
    direction_alignment_vs_profile_avg: float = 0.0
    scenario_deviation_class: str = "LOW_DEVIATION"


@dataclass(frozen=True)
class ProfileDispersionDiagnostic:
    condition_label: str
    forward_window: int
    profile_type: str
    scenario_count: int
    total_sample_size: int
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    forward_range_cv: float
    outcome_magnitude_cv: float
    direction_alignment_dispersion: float
    high_deviation_scenario_count: int
    moderate_deviation_scenario_count: int
    low_deviation_scenario_count: int
    dominant_deviation_class: str
    dispersion_driver_class: str
    profile_dispersion_class: str
    profile_research_readiness_class: str
    profile_dispersion_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ScenarioContributionRow:
    scenario_id: str
    profile_count: int
    total_observations: int
    average_sample_size: float
    average_forward_range_deviation: float
    average_outcome_magnitude_deviation: float
    average_direction_alignment_deviation: float
    high_deviation_profile_count: int
    moderate_deviation_profile_count: int
    low_deviation_profile_count: int
    high_deviation_profile_ratio: float
    dominant_deviation_class: str
    scenario_contribution_class: str
    scenario_dispersion_diagnostic: str


@dataclass(frozen=True)
class StateDispersionSummaryRow:
    condition_label: str
    profile_count: int
    research_ready_profile_count: int
    sample_constrained_profile_count: int
    high_dispersion_profile_count: int
    moderate_dispersion_profile_count: int
    stable_profile_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_dispersion: float
    average_high_deviation_scenario_count: float
    dominant_dispersion_class: str
    state_dispersion_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class WindowDispersionSummaryRow:
    forward_window: int
    profile_count: int
    research_ready_profile_count: int
    sample_constrained_profile_count: int
    high_dispersion_profile_count: int
    moderate_dispersion_profile_count: int
    stable_profile_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_dispersion: float
    average_high_deviation_scenario_count: float
    window_dispersion_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class AggregationCandidateProfile(ProfileDispersionDiagnostic):
    aggregation_candidate_rationale: str = ""


@dataclass(frozen=True)
class ScenarioSensitiveProfile(ProfileDispersionDiagnostic):
    scenario_sensitivity_rationale: str = ""


@dataclass(frozen=True)
class SampleConstrainedProfile(ProfileDispersionDiagnostic):
    sample_review_rationale: str = ""


@dataclass(frozen=True)
class H4ScenarioDispersionReviewSummary:
    timeframe: str
    input_profile_count: int
    research_ready_profile_count: int
    sample_constrained_profile_count: int
    aggregation_candidate_profile_count: int
    scenario_sensitive_profile_count: int
    high_dispersion_profile_count: int
    moderate_dispersion_profile_count: int
    stable_profile_count: int
    scenario_count: int
    high_contribution_scenario_count: int
    moderate_contribution_scenario_count: int
    low_contribution_scenario_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_dispersion: float
    h4_dispersion_profile: str
    h4_aggregation_readiness_flag: str
    h4_scenario_dispersion_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4ScenarioDispersionReviewResult:
    input_dir: Path
    output_dir: Path
    report_path: Path
    profiles_loaded: int = 0
    statistics_loaded: int = 0
    comparison_rows_loaded: int = 0
    profile_diagnostics: list[ProfileDispersionDiagnostic] = field(default_factory=list)
    scenario_contributions: list[ScenarioContributionRow] = field(default_factory=list)
    state_summaries: list[StateDispersionSummaryRow] = field(default_factory=list)
    window_summaries: list[WindowDispersionSummaryRow] = field(default_factory=list)
    aggregation_candidates: list[AggregationCandidateProfile] = field(default_factory=list)
    scenario_sensitive_profiles: list[ScenarioSensitiveProfile] = field(default_factory=list)
    sample_constrained_profiles: list[SampleConstrainedProfile] = field(default_factory=list)
    review_summary: H4ScenarioDispersionReviewSummary | None = None
    missing_optional_files: list[str] = field(default_factory=list)
