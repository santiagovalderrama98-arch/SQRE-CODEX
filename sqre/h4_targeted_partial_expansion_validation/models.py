"""Models for H4 targeted partial expansion validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PartialCandidate:
    candidate_id: str
    symbol: str
    timeframe: str
    sample_label: str
    feasibility_class: str
    coverage_ratio: float
    raw_file_path: str = ""
    raw_file_status: str = "MISSING"
    defined_start_date: str = ""
    defined_end_date: str = ""
    actual_start_date: str = ""
    actual_end_date: str = ""
    candidate_selection_status: str = "SELECTED"
    candidate_diagnostic: str = ""


@dataclass(frozen=True)
class PartialValidationRunSummary:
    candidate_id: str
    sample_label: str
    run_status: str
    event_detection_status: str
    market_structure_status: str
    market_states_status: str
    transition_engine_status: str
    research_engine_status: str
    price_outcome_status: str
    ohlc_rows: int
    event_count: int
    structure_count: int
    state_count: int
    transition_count: int
    condition_profile_count: int
    run_diagnostic: str


@dataclass(frozen=True)
class PartialStructureStateSummary:
    candidate_id: str
    sample_label: str
    ohlc_rows: int
    structure_count: int
    average_structure_duration: float
    average_structure_range_pips: float
    unique_state_count: int
    most_common_state: str
    state_diversity_profile: str
    structure_state_diagnostic: str


@dataclass(frozen=True)
class PartialTransitionSummary:
    candidate_id: str
    sample_label: str
    transition_count: int
    unique_transition_count: int
    most_common_transition: str
    directional_to_directional_count: int
    directional_to_rotation_count: int
    rotation_to_directional_count: int
    sample_transition_diagnostic: str


@dataclass(frozen=True)
class PartialPriceOutcomeSummary:
    candidate_id: str
    sample_label: str
    condition_profile_count: int
    research_ready_profile_count: int
    sample_constrained_profile_count: int
    scenario_sensitive_profile_count: int
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    price_outcome_diagnostic: str


@dataclass(frozen=True)
class BaselineMetrics:
    scenario_count: int = 0
    average_ohlc_rows: float = 0.0
    average_structure_count: float = 0.0
    average_state_count: float = 0.0
    average_transition_count: float = 0.0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0


@dataclass(frozen=True)
class PartialBaselineComparison:
    candidate_id: str
    sample_label: str
    baseline_scenario_count: int
    partial_ohlc_rows: int
    baseline_average_ohlc_rows: float
    partial_structure_count: int
    baseline_average_structure_count: float
    structure_count_vs_baseline_ratio: float
    partial_state_count: int
    baseline_average_state_count: float
    partial_transition_count: int
    baseline_average_transition_count: float
    partial_average_forward_range_pips: float
    baseline_average_forward_range_pips: float
    forward_range_vs_baseline_ratio: float
    partial_average_outcome_magnitude_pips: float
    baseline_average_outcome_magnitude_pips: float
    outcome_magnitude_vs_baseline_ratio: float
    partial_comparison_class: str
    partial_comparison_diagnostic: str


@dataclass(frozen=True)
class PartialSampleAdequacyRow:
    candidate_id: str
    sample_label: str
    coverage_ratio: float
    ohlc_rows: int
    structure_count: int
    state_count: int
    transition_count: int
    condition_profile_count: int
    sample_adequacy_class: str
    sample_adequacy_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TargetedPartialExpansionSummary:
    timeframe: str
    candidate_count: int
    validated_partial_candidate_count: int
    failed_candidate_count: int
    partial_sample_count: int
    baseline_scenario_count: int
    average_coverage_ratio: float
    partial_research_usable_count: int
    partial_limited_count: int
    partial_insufficient_count: int
    partial_unavailable_count: int
    h4_partial_expansion_profile: str
    h4_partial_expansion_readiness_flag: str
    h4_partial_expansion_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TargetedPartialExpansionResult:
    feasibility_dir: Path
    baseline_validation_dir: Path
    baseline_research_dir: Path
    output_dir: Path
    research_output_dir: Path
    report_path: Path
    candidates: list[PartialCandidate] = field(default_factory=list)
    run_summaries: list[PartialValidationRunSummary] = field(default_factory=list)
    structure_state_summaries: list[PartialStructureStateSummary] = field(default_factory=list)
    transition_summaries: list[PartialTransitionSummary] = field(default_factory=list)
    price_outcome_summaries: list[PartialPriceOutcomeSummary] = field(default_factory=list)
    baseline_comparisons: list[PartialBaselineComparison] = field(default_factory=list)
    sample_adequacy_rows: list[PartialSampleAdequacyRow] = field(default_factory=list)
    summary: H4TargetedPartialExpansionSummary | None = None
