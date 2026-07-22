from sqre.h4_transition_state_combined_context_review.models import CombinedContextInventoryRow
from sqre.h4_transition_state_combined_context_review.state_transition_alignment_review import build_alignment_review


def test_alignment_flags_scenario_sensitive_when_state_and_transition_high():
    row = CombinedContextInventoryRow(
        "CTX_1",
        "EURUSD",
        "H4",
        "A",
        "B",
        "A -> B",
        "12",
        "STATE_PROFILE_AVAILABLE",
        "TRANSITION_PROFILE_AVAILABLE",
        "STABLE",
        "STABLE",
        "HIGH_SCENARIO_SENSITIVE",
        "HIGH_SCENARIO_SENSITIVE",
        "PARTIAL_CONTEXT_AVAILABLE",
        "ok",
    )

    review = build_alignment_review([row])

    assert review[0].state_transition_alignment_class == "STATE_TRANSITION_ALIGNED_SCENARIO_SENSITIVE"
