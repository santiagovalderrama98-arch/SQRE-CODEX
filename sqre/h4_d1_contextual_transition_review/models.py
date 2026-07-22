"""Data models for H4/D1 contextual transition review."""

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
class H4ContextRow:
    context_id: str
    symbol: str
    h4_source_state: str
    h4_target_state: str
    h4_transition_label: str
    h4_forward_window: str
    h4_context_interpretation_class: str
    h4_context_readiness_flag: str
    h4_combined_dispersion_class: str
    h4_combined_sensitivity_class: str
    h4_scenario_id: str = ""
    start_date: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class D1ContextRow:
    d1_context_id: str
    d1_scenario_id: str
    d1_regime_label: str
    d1_context_label: str
    d1_state_profile: str
    d1_dispersion_class: str
    d1_sample_adequacy_class: str
    d1_readiness_flag: str
    start_date: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class ScenarioContextMapRow:
    scenario_context_id: str
    symbol: str
    h4_scenario_id: str
    d1_scenario_id: str
    d1_regime_label: str
    d1_context_label: str
    mapping_method: str
    mapping_confidence_class: str
    mapping_diagnostic: str


@dataclass(frozen=True)
class H4D1ContextInventoryRow:
    context_id: str
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_source_state: str
    h4_target_state: str
    h4_transition_label: str
    h4_forward_window: str
    h4_context_interpretation_class: str
    h4_context_readiness_flag: str
    h4_combined_dispersion_class: str
    h4_combined_sensitivity_class: str
    d1_regime_label: str
    d1_context_status: str
    d1_sample_adequacy_class: str
    d1_dispersion_class: str
    partial_context_status: str
    mapping_confidence_class: str
    context_inventory_diagnostic: str


@dataclass(frozen=True)
class D1RegimeContextReviewRow:
    context_id: str
    d1_regime_label: str
    d1_context_status: str
    d1_regime_count: int
    d1_sample_adequacy_class: str
    d1_dispersion_class: str
    d1_regime_sensitivity_class: str
    d1_context_interpretation_class: str
    d1_context_diagnostic: str


@dataclass(frozen=True)
class H4D1AlignmentReviewRow:
    context_id: str
    h4_source_state: str
    h4_target_state: str
    h4_transition_label: str
    h4_forward_window: str
    h4_context_interpretation_class: str
    h4_context_readiness_flag: str
    d1_context_interpretation_class: str
    d1_regime_label: str
    h4_d1_alignment_class: str
    h4_d1_alignment_diagnostic: str


@dataclass(frozen=True)
class ContextualDispersionReviewRow:
    context_id: str
    h4_transition_label: str
    h4_forward_window: str
    h4_combined_dispersion_class: str
    d1_dispersion_class: str
    d1_regime_label: str
    contextual_dispersion_class: str
    contextual_dispersion_driver: str
    contextual_dispersion_diagnostic: str


@dataclass(frozen=True)
class ContextualSensitivityReviewRow:
    context_id: str
    h4_combined_sensitivity_class: str
    d1_regime_sensitivity_class: str
    d1_regime_label: str
    contextual_sensitivity_class: str
    contextual_sensitivity_diagnostic: str


@dataclass(frozen=True)
class PartialContextIntegrationRow:
    context_id: str
    partial_sample_id: str
    partial_sample_label: str
    partial_interpretation_class: str
    partial_readiness_flag: str
    partial_context_use_class: str
    h4_d1_partial_use_class: str
    partial_context_diagnostic: str


@dataclass(frozen=True)
class H4D1ContextualInterpretationRow:
    context_id: str
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_source_state: str
    h4_target_state: str
    h4_transition_label: str
    h4_forward_window: str
    d1_regime_label: str
    h4_d1_alignment_class: str
    contextual_dispersion_class: str
    contextual_sensitivity_class: str
    h4_d1_partial_use_class: str
    h4_d1_contextual_interpretation_class: str
    h4_d1_contextual_readiness_flag: str
    h4_d1_contextual_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1ContextualTransitionSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    context_count: int
    mapped_context_count: int
    unmapped_context_count: int
    d1_regime_count: int
    d1_context_reinforces_h4_dispersion_count: int
    d1_context_segments_h4_dispersion_count: int
    d1_context_does_not_reduce_h4_dispersion_count: int
    d1_reinforces_h4_scenario_sensitivity_count: int
    d1_contextualizes_h4_scenario_sensitivity_count: int
    input_limited_count: int
    sample_constrained_count: int
    ready_for_contextual_reference_count: int
    requires_scenario_and_regime_interpretation_count: int
    requires_sample_adequacy_review_count: int
    requires_input_completeness_review_count: int
    dominant_h4_d1_contextual_interpretation: str
    h4_d1_contextual_profile: str
    h4_d1_contextual_readiness_flag: str
    h4_d1_contextual_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1ContextualTransitionReviewResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    scenario_context_map: list[ScenarioContextMapRow] = field(default_factory=list)
    context_inventory: list[H4D1ContextInventoryRow] = field(default_factory=list)
    regime_reviews: list[D1RegimeContextReviewRow] = field(default_factory=list)
    alignment_reviews: list[H4D1AlignmentReviewRow] = field(default_factory=list)
    dispersion_reviews: list[ContextualDispersionReviewRow] = field(default_factory=list)
    sensitivity_reviews: list[ContextualSensitivityReviewRow] = field(default_factory=list)
    partial_integrations: list[PartialContextIntegrationRow] = field(default_factory=list)
    interpretation_rows: list[H4D1ContextualInterpretationRow] = field(default_factory=list)
    summary: H4D1ContextualTransitionSummary | None = None
