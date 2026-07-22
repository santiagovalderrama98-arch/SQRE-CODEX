"""Models for H4 transition/state combined context review."""

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
class StateContext:
    state_label: str
    forward_window: str
    profile_status: str = "STATE_PROFILE_UNAVAILABLE"
    dispersion_status: str = "STATE_DISPERSION_UNAVAILABLE"
    sensitivity_status: str = "STATE_SENSITIVITY_UNAVAILABLE"
    readiness_flag: str = "STATE_READINESS_UNAVAILABLE"
    sample_size: int = 0


@dataclass(frozen=True)
class TransitionContext:
    source_state: str
    target_state: str
    transition_label: str
    forward_window: str
    profile_status: str = "TRANSITION_PROFILE_UNAVAILABLE"
    dispersion_status: str = "TRANSITION_DISPERSION_UNAVAILABLE"
    sensitivity_status: str = "TRANSITION_SENSITIVITY_UNAVAILABLE"
    readiness_flag: str = "TRANSITION_READINESS_UNAVAILABLE"
    sample_size: int = 0
    near_aggregation_candidate_flag: str = "false"


@dataclass(frozen=True)
class PartialContext:
    partial_sample_id: str = ""
    partial_sample_label: str = "PARTIAL_SAMPLE"
    partial_interpretation_class: str = "PARTIAL_CONTEXT_UNAVAILABLE"
    partial_readiness_flag: str = "PARTIAL_CONTEXT_UNAVAILABLE"
    partial_caveat_class: str = "PARTIAL_CONTEXT_UNAVAILABLE"


@dataclass(frozen=True)
class CombinedContextInventoryRow:
    context_id: str
    symbol: str
    timeframe: str
    source_state: str
    target_state: str
    transition_label: str
    forward_window: str
    state_profile_status: str
    transition_profile_status: str
    state_dispersion_status: str
    transition_dispersion_status: str
    state_sensitivity_status: str
    transition_sensitivity_status: str
    partial_context_status: str
    context_inventory_diagnostic: str


@dataclass(frozen=True)
class AlignmentReviewRow:
    context_id: str
    source_state: str
    target_state: str
    transition_label: str
    forward_window: str
    state_readiness_flag: str
    transition_readiness_flag: str
    state_dispersion_class: str
    transition_dispersion_class: str
    state_transition_alignment_class: str
    state_transition_alignment_diagnostic: str


@dataclass(frozen=True)
class CombinedDispersionReviewRow:
    context_id: str
    source_state: str
    target_state: str
    transition_label: str
    forward_window: str
    state_dispersion_class: str
    transition_dispersion_class: str
    combined_dispersion_class: str
    combined_dispersion_driver: str
    combined_dispersion_diagnostic: str


@dataclass(frozen=True)
class CombinedSensitivityReviewRow:
    context_id: str
    source_state: str
    target_state: str
    transition_label: str
    forward_window: str
    state_sensitivity_class: str
    transition_sensitivity_class: str
    near_aggregation_candidate_flag: str
    combined_sensitivity_class: str
    combined_sensitivity_diagnostic: str


@dataclass(frozen=True)
class PartialContextCaveatRow:
    context_id: str
    partial_sample_id: str
    partial_sample_label: str
    partial_interpretation_class: str
    partial_readiness_flag: str
    partial_caveat_class: str
    partial_context_use_class: str
    partial_context_diagnostic: str


@dataclass(frozen=True)
class CombinedContextInterpretationRow:
    context_id: str
    symbol: str
    timeframe: str
    source_state: str
    target_state: str
    transition_label: str
    forward_window: str
    state_transition_alignment_class: str
    combined_dispersion_class: str
    combined_sensitivity_class: str
    partial_context_use_class: str
    combined_context_interpretation_class: str
    combined_context_readiness_flag: str
    combined_context_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TransitionStateCombinedContextSummary:
    timeframe: str
    context_count: int
    aligned_scenario_sensitive_count: int
    mixed_diagnostics_count: int
    combined_high_dispersion_count: int
    combined_sample_constrained_count: int
    combined_baseline_unavailable_count: int
    combined_scenario_sensitive_count: int
    descriptively_stable_count: int
    input_limited_count: int
    partial_context_limited_support_count: int
    ready_for_context_reference_count: int
    requires_scenario_level_interpretation_count: int
    requires_sample_adequacy_review_count: int
    requires_input_completeness_review_count: int
    dominant_combined_context_interpretation: str
    h4_transition_state_context_profile: str
    h4_transition_state_context_readiness_flag: str
    h4_transition_state_context_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TransitionStateCombinedContextReviewResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    context_inventory: list[CombinedContextInventoryRow] = field(default_factory=list)
    alignment_reviews: list[AlignmentReviewRow] = field(default_factory=list)
    dispersion_reviews: list[CombinedDispersionReviewRow] = field(default_factory=list)
    sensitivity_reviews: list[CombinedSensitivityReviewRow] = field(default_factory=list)
    partial_caveats: list[PartialContextCaveatRow] = field(default_factory=list)
    interpretation_rows: list[CombinedContextInterpretationRow] = field(default_factory=list)
    summary: H4TransitionStateCombinedContextSummary | None = None
