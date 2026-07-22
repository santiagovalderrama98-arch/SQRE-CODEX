"""Pipeline for H4 transition/state combined context review."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.combined_context_builder import (
    build_combined_context_inventory,
)
from sqre.h4_transition_state_combined_context_review.combined_dispersion_review import (
    build_combined_dispersion_review,
)
from sqre.h4_transition_state_combined_context_review.combined_sensitivity_review import (
    build_combined_sensitivity_review,
)
from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.context_interpretation import (
    build_context_interpretation_matrix,
)
from sqre.h4_transition_state_combined_context_review.findings import build_summary
from sqre.h4_transition_state_combined_context_review.loader import build_source_inventory
from sqre.h4_transition_state_combined_context_review.models import (
    H4TransitionStateCombinedContextReviewResult,
    PartialContext,
)
from sqre.h4_transition_state_combined_context_review.partial_caveat_integrator import (
    build_partial_caveat_integration,
)
from sqre.h4_transition_state_combined_context_review.partial_context_loader import load_partial_context
from sqre.h4_transition_state_combined_context_review.reports import write_review_outputs
from sqre.h4_transition_state_combined_context_review.state_context_loader import (
    load_state_contexts,
    load_state_summary_context,
)
from sqre.h4_transition_state_combined_context_review.state_transition_alignment_review import (
    build_alignment_review,
)
from sqre.h4_transition_state_combined_context_review.transition_context_loader import (
    load_transition_contexts,
    load_transition_summary_context,
)


def run_h4_transition_state_combined_context_review(
    config: H4TransitionStateCombinedContextReviewConfig | None = None,
) -> H4TransitionStateCombinedContextReviewResult:
    active_config = config or H4TransitionStateCombinedContextReviewConfig()
    source_inventory = build_source_inventory(active_config)
    states = load_state_contexts(active_config)
    state_summary = load_state_summary_context(active_config)
    transitions = load_transition_contexts(active_config)
    if not transitions:
        transitions = [load_transition_summary_context(active_config)]
    partial = load_partial_context(active_config) if active_config.allow_partial_context else PartialContext()
    context_inventory = build_combined_context_inventory(
        transitions,
        states,
        state_summary,
        partial,
        active_config,
    )
    alignment_reviews = build_alignment_review(context_inventory)
    dispersion_reviews = build_combined_dispersion_review(context_inventory)
    sensitivity_reviews = build_combined_sensitivity_review(context_inventory)
    partial_caveats = build_partial_caveat_integration(context_inventory, partial)
    interpretations = build_context_interpretation_matrix(
        context_inventory,
        alignment_reviews,
        dispersion_reviews,
        sensitivity_reviews,
        partial_caveats,
    )
    summary = build_summary(interpretations, active_config)
    result = H4TransitionStateCombinedContextReviewResult(
        output_dir=active_config.output_dir,
        report_path=active_config.report_path,
        source_inventory=source_inventory,
        context_inventory=context_inventory,
        alignment_reviews=alignment_reviews,
        dispersion_reviews=dispersion_reviews,
        sensitivity_reviews=sensitivity_reviews,
        partial_caveats=partial_caveats,
        interpretation_rows=interpretations,
        summary=summary,
    )
    return write_review_outputs(result)
