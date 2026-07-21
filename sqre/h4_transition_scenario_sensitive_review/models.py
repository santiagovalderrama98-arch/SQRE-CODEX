"""Models for H4 transition scenario-sensitive profile review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ScenarioSensitiveTransitionProfileInput:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    profile_type: str = ""
    scenario_count: int = 0
    total_sample_size: int = 0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    average_direction_alignment_rate: float = 0.0
    forward_range_cv: float = 0.0
    outcome_magnitude_cv: float = 0.0
    direction_alignment_dispersion: float = 0.0
    high_deviation_scenario_count: int = 0
    moderate_deviation_scenario_count: int = 0
    low_deviation_scenario_count: int = 0
    dominant_deviation_class: str = "LOW_DEVIATION"
    dispersion_driver_class: str = "LOW_DISPERSION"
    profile_dispersion_class: str = "STABLE_DESCRIPTIVE"
    transition_profile_readiness_class: str = ""
    profile_dispersion_diagnostic: str = ""
    recommended_follow_up: str = ""


@dataclass(frozen=True)
class ScenarioComparisonInput:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    scenario_id: str
    sample_size: int = 0
    forward_range_vs_profile_avg: float = 0.0
    outcome_magnitude_vs_profile_avg: float = 0.0
    direction_alignment_vs_profile_avg: float = 0.0
    scenario_deviation_class: str = "LOW_DEVIATION"
    scenario_comparison_diagnostic: str = ""


@dataclass(frozen=True)
class ScenarioBreakdownInput:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    profile_type: str
    scenario_id: str
    timeframe: str = "H4"
    sample_size: int = 0
    average_forward_close_return_pips: float = 0.0
    median_forward_close_return_pips: float = 0.0
    average_forward_range_pips: float = 0.0
    average_favorable_displacement_pips: float = 0.0
    average_adverse_displacement_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    direction_alignment_rate: float = 0.0
    sample_adequacy_flag: str = ""
    scenario_observation_diagnostic: str = ""


@dataclass(frozen=True)
class ProfileReviewRow:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
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
    primary_deviating_metric: str
    transition_sensitivity_class: str
    focus_transition_flag: str
    near_aggregation_candidate_flag: str
    profile_review_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ScenarioDeviationDetailRow:
    condition_label: str
    source_state: str
    target_state: str
    transition_family: str
    forward_window: int
    scenario_id: str
    sample_size: int
    forward_range_vs_profile_avg: float
    outcome_magnitude_vs_profile_avg: float
    direction_alignment_vs_profile_avg: float
    scenario_deviation_class: str
    primary_scenario_deviation_metric: str
    scenario_deviation_intensity_class: str
    scenario_deviation_diagnostic: str


@dataclass(frozen=True)
class ScenarioRecurrentDeviationSummary:
    scenario_id: str
    scenario_profile_count: int
    high_deviation_profile_count: int
    moderate_deviation_profile_count: int
    low_deviation_profile_count: int
    average_forward_range_deviation: float
    average_outcome_magnitude_deviation: float
    average_direction_alignment_deviation: float
    most_common_primary_deviation_metric: str
    scenario_recurrent_deviation_class: str
    scenario_review_diagnostic: str


@dataclass(frozen=True)
class TransitionGroupSensitivitySummary:
    group_value: str
    profile_count: int
    high_sensitivity_profile_count: int
    moderate_sensitivity_profile_count: int
    low_sensitivity_profile_count: int
    focus_profile_count: int
    near_aggregation_candidate_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_dispersion: float
    most_common_dispersion_driver: str
    sensitivity_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ForwardWindowSensitivitySummary:
    forward_window: int
    profile_count: int
    high_sensitivity_profile_count: int
    moderate_sensitivity_profile_count: int
    low_sensitivity_profile_count: int
    focus_profile_count: int
    near_aggregation_candidate_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_dispersion: float
    most_common_dispersion_driver: str
    window_sensitivity_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class NearAggregationCandidate(ProfileReviewRow):
    near_candidate_rationale: str = ""


@dataclass(frozen=True)
class FocusProfileReview(ProfileReviewRow):
    focus_profile_rationale: str = ""


@dataclass(frozen=True)
class H4TransitionScenarioSensitiveReviewSummary:
    timeframe: str
    scenario_sensitive_profile_count: int
    reviewed_profile_count: int
    focus_profile_count: int
    high_sensitivity_profile_count: int
    moderate_sensitivity_profile_count: int
    low_sensitivity_profile_count: int
    near_aggregation_candidate_count: int
    scenario_count: int
    high_recurrent_deviation_scenario_count: int
    moderate_recurrent_deviation_scenario_count: int
    low_recurrent_deviation_scenario_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_dispersion: float
    dominant_dispersion_driver: str
    h4_transition_scenario_sensitive_profile: str
    h4_review_readiness_flag: str
    h4_transition_scenario_sensitive_review_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TransitionScenarioSensitiveReviewResult:
    dispersion_review_dir: Path
    transition_deep_dive_dir: Path
    output_dir: Path
    report_path: Path
    scenario_sensitive_profiles_loaded: int = 0
    comparison_rows_loaded: int = 0
    breakdown_rows_loaded: int = 0
    reviewed_profiles: list[ProfileReviewRow] = field(default_factory=list)
    focus_profiles: list[FocusProfileReview] = field(default_factory=list)
    scenario_details: list[ScenarioDeviationDetailRow] = field(default_factory=list)
    scenario_summaries: list[ScenarioRecurrentDeviationSummary] = field(default_factory=list)
    family_summaries: list[TransitionGroupSensitivitySummary] = field(default_factory=list)
    source_state_summaries: list[TransitionGroupSensitivitySummary] = field(default_factory=list)
    target_state_summaries: list[TransitionGroupSensitivitySummary] = field(default_factory=list)
    window_summaries: list[ForwardWindowSensitivitySummary] = field(default_factory=list)
    near_candidates: list[NearAggregationCandidate] = field(default_factory=list)
    review_summary: H4TransitionScenarioSensitiveReviewSummary | None = None
    missing_optional_files: list[str] = field(default_factory=list)
