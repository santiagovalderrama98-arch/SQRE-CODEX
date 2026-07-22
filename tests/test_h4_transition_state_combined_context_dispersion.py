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


def test_dispersion_uses_transition_evidence_when_state_baseline_missing():
    row = CombinedContextInventoryRow(
        "CTX_1",
        "EURUSD",
        "H4",
        "A",
        "B",
        "A -> B",
        "12",
        "STATE_PROFILE_UNAVAILABLE",
        "TRANSITION_PROFILE_AVAILABLE",
        "STATE_DISPERSION_UNAVAILABLE",
        "HIGH_DISPERSION",
        "LOW",
        "LOW",
        "PARTIAL_CONTEXT_AVAILABLE",
        "ok",
    )

    review = build_combined_dispersion_review([row])

    assert review[0].combined_dispersion_class == "COMBINED_HIGH_DISPERSION"
    assert review[0].combined_dispersion_driver == "TRANSITION_DRIVEN"


def test_dispersion_marks_baseline_unavailable_only_when_both_inputs_missing():
    row = CombinedContextInventoryRow(
        "CTX_1",
        "EURUSD",
        "H4",
        "A",
        "B",
        "A -> B",
        "12",
        "STATE_PROFILE_UNAVAILABLE",
        "TRANSITION_PROFILE_UNAVAILABLE",
        "STATE_DISPERSION_UNAVAILABLE",
        "TRANSITION_DISPERSION_UNAVAILABLE",
        "LOW",
        "LOW",
        "PARTIAL_CONTEXT_AVAILABLE",
        "ok",
    )

    review = build_combined_dispersion_review([row])

    assert review[0].combined_dispersion_class == "COMBINED_BASELINE_UNAVAILABLE"
    assert review[0].combined_dispersion_driver == "INPUT_LIMITED"
