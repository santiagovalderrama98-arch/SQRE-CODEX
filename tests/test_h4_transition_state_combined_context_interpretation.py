from sqre.h4_transition_state_combined_context_review.context_interpretation import (
    build_context_interpretation_matrix,
)
from sqre.h4_transition_state_combined_context_review.models import (
    AlignmentReviewRow,
    CombinedContextInventoryRow,
    CombinedDispersionReviewRow,
    CombinedSensitivityReviewRow,
    PartialContextCaveatRow,
)


def test_interpretation_reinforces_scenario_level_context():
    inventory = _inventory()
    rows = build_context_interpretation_matrix(
        [inventory],
        [
            AlignmentReviewRow(
                "CTX_1",
                "A",
                "B",
                "A -> B",
                "12",
                "HIGH",
                "HIGH",
                "STABLE",
                "STABLE",
                "STATE_TRANSITION_ALIGNED_SCENARIO_SENSITIVE",
                "aligned",
            )
        ],
        [CombinedDispersionReviewRow("CTX_1", "A", "B", "A -> B", "12", "STABLE", "STABLE", "COMBINED_STABLE_DESCRIPTIVE", "MIXED_DRIVEN", "stable")],
        [CombinedSensitivityReviewRow("CTX_1", "A", "B", "A -> B", "12", "HIGH", "HIGH", "false", "COMBINED_SCENARIO_SENSITIVE", "high")],
        [PartialContextCaveatRow("CTX_1", "P1", "PARTIAL_SAMPLE", "LIMITED", "LIMITED", "OK", "PARTIAL_CONTEXT_LIMITED_SUPPORT", "limited")],
    )

    assert rows[0].combined_context_interpretation_class == "CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION"
    assert rows[0].combined_context_readiness_flag == "REQUIRES_SCENARIO_LEVEL_INTERPRETATION"


def _inventory() -> CombinedContextInventoryRow:
    return CombinedContextInventoryRow(
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
        "HIGH",
        "HIGH",
        "PARTIAL_CONTEXT_AVAILABLE",
        "ok",
    )
