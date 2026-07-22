"""Models for H4 partial sample complementary dispersion review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SourceInventoryRow:
    source_name: str
    source_type: str
    path: str
    exists: bool
    load_status: str
    rows_loaded: int
    diagnostic: str


@dataclass(frozen=True)
class PartialSampleReviewRow:
    candidate_id: str
    sample_label: str
    coverage_ratio: float
    run_status: str
    sample_adequacy_class: str
    partial_comparison_class: str
    condition_profile_count: int
    partial_sample_status: str
    partial_sample_diagnostic: str


@dataclass(frozen=True)
class BaselineDispersionSnapshot:
    state_dispersion_profile: str = "BASELINE_UNAVAILABLE"
    state_readiness_flag: str = "BASELINE_UNAVAILABLE"
    transition_dispersion_profile: str = "BASELINE_UNAVAILABLE"
    transition_readiness_flag: str = "BASELINE_UNAVAILABLE"
    scenario_sensitive_profile: str = "BASELINE_UNAVAILABLE"
    high_sensitivity_profile_count: int = 0
    near_aggregation_candidate_count: int = 0


@dataclass(frozen=True)
class PartialStructureStateSnapshot:
    candidate_id: str
    sample_label: str
    partial_state_profile: str
    partial_unique_state_count: int
    partial_most_common_state: str


@dataclass(frozen=True)
class PartialTransitionSnapshot:
    candidate_id: str
    sample_label: str
    partial_most_common_transition: str
    partial_unique_transition_count: int


@dataclass(frozen=True)
class PartialStateComplementReviewRow:
    candidate_id: str
    sample_label: str
    partial_state_profile: str
    partial_unique_state_count: int
    partial_most_common_state: str
    baseline_state_dispersion_profile: str
    baseline_state_readiness_flag: str
    partial_state_consistency_class: str
    partial_state_diagnostic: str


@dataclass(frozen=True)
class PartialTransitionComplementReviewRow:
    candidate_id: str
    sample_label: str
    partial_most_common_transition: str
    partial_unique_transition_count: int
    baseline_transition_dispersion_profile: str
    baseline_transition_readiness_flag: str
    partial_transition_consistency_class: str
    partial_transition_diagnostic: str


@dataclass(frozen=True)
class PartialSensitivityComplementReviewRow:
    candidate_id: str
    sample_label: str
    baseline_scenario_sensitive_profile: str
    baseline_high_sensitivity_profile_count: int
    baseline_near_aggregation_candidate_count: int
    partial_comparison_class: str
    partial_condition_profile_count: int
    partial_sensitivity_interpretation: str
    partial_sensitivity_diagnostic: str


@dataclass(frozen=True)
class PartialBaselineInterpretationRow:
    candidate_id: str
    sample_label: str
    baseline_scenario_count: int
    coverage_ratio: float
    condition_profile_count: int
    sample_adequacy_class: str
    partial_comparison_class: str
    state_consistency_class: str
    transition_consistency_class: str
    sensitivity_interpretation: str
    partial_baseline_interpretation_class: str
    partial_baseline_interpretation_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class PartialSampleCaveatRow:
    candidate_id: str
    sample_label: str
    coverage_ratio: float
    baseline_scenario_count: int
    partial_sample_caveat_class: str
    partial_sample_caveat_diagnostic: str


@dataclass(frozen=True)
class H4PartialComplementaryDispersionSummary:
    timeframe: str
    candidate_count: int
    reviewed_partial_sample_count: int
    complementary_support_count: int
    consistent_but_limited_count: int
    divergent_count: int
    inconclusive_count: int
    unavailable_count: int
    baseline_scenario_count: int
    average_coverage_ratio: float
    average_condition_profile_count: float
    dominant_partial_baseline_interpretation: str
    h4_partial_complementary_profile: str
    h4_partial_complementary_readiness_flag: str
    h4_partial_complementary_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4PartialComplementaryDispersionReviewResult:
    partial_validation_dir: Path
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    partial_samples: list[PartialSampleReviewRow] = field(default_factory=list)
    state_reviews: list[PartialStateComplementReviewRow] = field(default_factory=list)
    transition_reviews: list[PartialTransitionComplementReviewRow] = field(default_factory=list)
    sensitivity_reviews: list[PartialSensitivityComplementReviewRow] = field(default_factory=list)
    interpretation_rows: list[PartialBaselineInterpretationRow] = field(default_factory=list)
    caveat_rows: list[PartialSampleCaveatRow] = field(default_factory=list)
    summary: H4PartialComplementaryDispersionSummary | None = None
