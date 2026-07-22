from sqre.h4_transition_state_combined_context_review.models import CombinedContextInventoryRow, PartialContext
from sqre.h4_transition_state_combined_context_review.partial_caveat_integrator import build_partial_caveat_integration


def test_partial_caveat_flags_limited_support():
    context = CombinedContextInventoryRow(
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
        "LOW",
        "LOW",
        "PARTIAL_CONTEXT_AVAILABLE",
        "ok",
    )
    partial = PartialContext(
        "P1",
        "PARTIAL_SAMPLE",
        "COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED",
        "PARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION",
        "PARTIAL_SAMPLE_CAVEAT_ACCEPTABLE",
    )

    review = build_partial_caveat_integration([context], partial)

    assert review[0].partial_context_use_class == "PARTIAL_CONTEXT_LIMITED_SUPPORT"
