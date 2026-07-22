"""Pipeline for Phase 7.5.14 H4/D1 contextual transition review."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.contextual_dispersion_review import build_contextual_dispersion_review
from sqre.h4_d1_contextual_transition_review.contextual_interpretation import build_contextual_interpretation_matrix
from sqre.h4_d1_contextual_transition_review.contextual_sensitivity_review import build_contextual_sensitivity_review
from sqre.h4_d1_contextual_transition_review.d1_context_loader import load_d1_contexts
from sqre.h4_d1_contextual_transition_review.d1_regime_context_review import (
    build_d1_regime_context_review,
    build_h4_d1_context_inventory,
)
from sqre.h4_d1_contextual_transition_review.findings import build_summary
from sqre.h4_d1_contextual_transition_review.h4_context_loader import load_h4_contexts
from sqre.h4_d1_contextual_transition_review.h4_d1_alignment_review import build_h4_d1_alignment_review
from sqre.h4_d1_contextual_transition_review.loader import build_source_inventory
from sqre.h4_d1_contextual_transition_review.models import H4D1ContextualTransitionReviewResult
from sqre.h4_d1_contextual_transition_review.partial_context_integrator import (
    build_partial_context_integration,
    partial_context_status,
)
from sqre.h4_d1_contextual_transition_review.reports import write_review_outputs
from sqre.h4_d1_contextual_transition_review.scenario_context_mapper import build_scenario_context_map


def run_h4_d1_contextual_transition_review(
    config: H4D1ContextualTransitionReviewConfig | None = None,
) -> H4D1ContextualTransitionReviewResult:
    active_config = config or H4D1ContextualTransitionReviewConfig()
    source_inventory = build_source_inventory(active_config)
    h4_rows = load_h4_contexts(active_config)
    d1_rows = load_d1_contexts(active_config)
    scenario_map = build_scenario_context_map(h4_rows, d1_rows, active_config)
    inventory = build_h4_d1_context_inventory(
        h4_rows,
        d1_rows,
        scenario_map,
        partial_context_status(active_config),
        active_config,
    )
    regime_reviews = build_d1_regime_context_review(inventory, d1_rows)
    alignment_reviews = build_h4_d1_alignment_review(inventory, regime_reviews)
    dispersion_reviews = build_contextual_dispersion_review(inventory, regime_reviews)
    sensitivity_reviews = build_contextual_sensitivity_review(inventory, regime_reviews)
    partial_integrations = build_partial_context_integration(inventory, active_config)
    interpretations = build_contextual_interpretation_matrix(
        inventory,
        alignment_reviews,
        dispersion_reviews,
        sensitivity_reviews,
        partial_integrations,
    )
    summary = build_summary(interpretations, scenario_map, active_config)
    result = H4D1ContextualTransitionReviewResult(
        output_dir=active_config.output_dir,
        report_path=active_config.report_path,
        source_inventory=source_inventory,
        scenario_context_map=scenario_map,
        context_inventory=inventory,
        regime_reviews=regime_reviews,
        alignment_reviews=alignment_reviews,
        dispersion_reviews=dispersion_reviews,
        sensitivity_reviews=sensitivity_reviews,
        partial_integrations=partial_integrations,
        interpretation_rows=interpretations,
        summary=summary,
    )
    return write_review_outputs(result)
