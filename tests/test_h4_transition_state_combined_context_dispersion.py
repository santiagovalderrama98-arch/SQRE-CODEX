from sqre.h4_transition_state_combined_context_review.combined_dispersion_review import (
    build_combined_dispersion_review,
)
from sqre.h4_transition_state_combined_context_review.models import CombinedContextInventoryRow


def test_dispersion_flags_high_with_state_driver():
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
        "HIGH_DISPERSION",
        "STABLE_DESCRIPTIVE",
        "LOW",
        "LOW",
        "PARTIAL_CONTEXT_AVAILABLE",
        "ok",
    )

    review = build_combined_dispersion_review([row])

    assert review[0].combined_dispersion_class == "COMBINED_HIGH_DISPERSION"
    assert review[0].combined_dispersion_driver == "STATE_DRIVEN"
