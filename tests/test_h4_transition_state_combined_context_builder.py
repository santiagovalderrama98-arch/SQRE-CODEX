from sqre.h4_transition_state_combined_context_review.combined_context_builder import (
    build_combined_context_inventory,
)
from sqre.h4_transition_state_combined_context_review.config import H4TransitionStateCombinedContextReviewConfig
from sqre.h4_transition_state_combined_context_review.models import PartialContext, StateContext, TransitionContext


def test_builder_matches_transition_source_state_to_state_context():
    transition = TransitionContext("EXPANSION", "CONSOLIDATION", "EXPANSION -> CONSOLIDATION", "12")
    states = {("EXPANSION", "12"): StateContext("EXPANSION", "12", sensitivity_status="HIGH_SCENARIO_SENSITIVE")}
    partial = PartialContext(partial_interpretation_class="COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED")

    rows = build_combined_context_inventory(
        [transition],
        states,
        StateContext("STATE_CONTEXT", ""),
        partial,
        H4TransitionStateCombinedContextReviewConfig(),
    )

    assert rows[0].context_id == "CTX_000001"
    assert rows[0].state_sensitivity_status == "HIGH_SCENARIO_SENSITIVE"
