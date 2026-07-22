from sqre.h4_transition_state_combined_context_review.combined_sensitivity_review import (
    build_combined_sensitivity_review,
)
from sqre.h4_transition_state_combined_context_review.models import CombinedContextInventoryRow


def test_sensitivity_flags_partial_scenario_sensitive():
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
        "LOW",
        "PARTIAL_CONTEXT_AVAILABLE",
        "ok",
    )

    review = build_combined_sensitivity_review([row])

    assert review[0].combined_sensitivity_class == "COMBINED_PARTIALLY_SCENARIO_SENSITIVE"
