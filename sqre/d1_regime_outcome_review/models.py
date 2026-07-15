"""Models for D1 regime outcome review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_PROFILE_COLUMNS = [
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Regime_Count",
    "Total_Sample_Size",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
    "Regime_Sensitivity_Flag",
]


@dataclass(frozen=True)
class ConditionProfileInput:
    condition_type: str
    condition_label: str
    forward_window: int
    regime_count: int
    regimes_present: str
    scenario_count: int
    total_sample_size: int
    average_sample_size_per_regime: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    forward_range_cv: float
    outcome_magnitude_cv: float
    direction_alignment_cv: float
    regime_sensitivity_flag: str


@dataclass(frozen=True)
class ConditionQualityInventoryRow:
    condition_type: str
    condition_label: str
    forward_window: int
    regime_count: int
    regimes_present: str
    scenario_count: int
    total_sample_size: int
    average_sample_size_per_regime: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    forward_range_cv: float
    outcome_magnitude_cv: float
    direction_alignment_cv: float
    sample_adequacy_class: str
    regime_coverage_class: str
    dispersion_class: str
    sensitivity_class: str
    condition_research_class: str
    condition_review_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ConditionLabelSummary:
    condition_label: str
    profile_count: int
    research_ready_profile_count: int
    regime_sensitive_profile_count: int
    low_sample_profile_count: int
    limited_coverage_profile_count: int
    average_total_sample_size: float
    average_regime_count: float
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    dominant_condition_research_class: str
    state_condition_diagnostic: str = ""
    transition_condition_diagnostic: str = ""
    recommended_follow_up: str = ""


@dataclass(frozen=True)
class DispersionSummary:
    condition_type: str
    profile_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    low_dispersion_profile_count: int
    moderate_dispersion_profile_count: int
    high_dispersion_profile_count: int
    stable_sensitivity_profile_count: int
    moderate_sensitivity_profile_count: int
    high_sensitivity_profile_count: int
    outcome_dispersion_diagnostic: str


@dataclass(frozen=True)
class SampleAdequacySummary:
    scope: str
    profile_count: int
    adequate_profile_count: int
    low_sample_profile_count: int
    limited_coverage_profile_count: int
    research_ready_profile_count: int
    regime_sensitive_profile_count: int
    adequate_profile_ratio: float
    low_sample_profile_ratio: float
    limited_coverage_profile_ratio: float
    research_ready_profile_ratio: float
    sample_adequacy_diagnostic: str


@dataclass(frozen=True)
class D1OutcomeReviewSummary:
    timeframe: str
    input_profile_count: int
    research_ready_profile_count: int
    regime_sensitive_profile_count: int
    low_sample_profile_count: int
    limited_coverage_profile_count: int
    high_dispersion_profile_count: int
    state_profile_count: int
    transition_profile_count: int
    research_ready_state_profile_count: int
    research_ready_transition_profile_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_rate: float
    sample_adequacy_profile: str
    outcome_dispersion_profile: str
    regime_sensitivity_profile: str
    d1_outcome_review_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class D1RegimeOutcomeReviewResult:
    input_dir: Path
    output_dir: Path
    report_path: Path
    profiles_loaded: int = 0
    inventory_rows: list[ConditionQualityInventoryRow] = field(default_factory=list)
    research_ready_profiles: list[ConditionQualityInventoryRow] = field(default_factory=list)
    regime_sensitive_profiles: list[ConditionQualityInventoryRow] = field(default_factory=list)
    low_sample_profiles: list[ConditionQualityInventoryRow] = field(default_factory=list)
    limited_coverage_profiles: list[ConditionQualityInventoryRow] = field(default_factory=list)
    state_summaries: list[ConditionLabelSummary] = field(default_factory=list)
    transition_summaries: list[ConditionLabelSummary] = field(default_factory=list)
    dispersion_summaries: list[DispersionSummary] = field(default_factory=list)
    sample_adequacy_summaries: list[SampleAdequacySummary] = field(default_factory=list)
    review_summary: D1OutcomeReviewSummary | None = None
