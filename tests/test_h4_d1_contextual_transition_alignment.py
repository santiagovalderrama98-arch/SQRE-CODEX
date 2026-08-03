from sqre.h4_d1_contextual_transition_review.h4_d1_alignment_review import build_h4_d1_alignment_review
from sqre.h4_d1_contextual_transition_review.models import D1RegimeContextReviewRow, H4D1ContextInventoryRow


def _inventory(confidence: str) -> H4D1ContextInventoryRow:
    return H4D1ContextInventoryRow(
        "CTX_1", "EURUSD", "H4", "D1", "A", "B", "A -> B", "12",
        "CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION", "REQUIRES_SCENARIO_LEVEL_INTERPRETATION",
        "COMBINED_HIGH_DISPERSION", "COMBINED_SCENARIO_SENSITIVE", "TREND_REGIME",
        "D1_CONTEXT_AVAILABLE", "SAMPLE_ADEQUATE", "HIGH_DISPERSION", "PARTIAL_CONTEXT_UNAVAILABLE",
        confidence, "ok",
    )


def _d1() -> D1RegimeContextReviewRow:
    return D1RegimeContextReviewRow("CTX_1", "TREND_REGIME", "D1_CONTEXT_AVAILABLE", 1, "OK", "HIGH", "D1_REGIME_SENSITIVE", "D1_CONTEXT_REGIME_SENSITIVE", "ok")


def test_alignment_classifies_aligned_scenario_regime_sensitive():
    rows = build_h4_d1_alignment_review([_inventory("HIGH_CONFIDENCE_MAPPING")], [_d1()])

    assert rows[0].h4_d1_alignment_class == "H4_D1_ALIGNED_SCENARIO_AND_REGIME_SENSITIVE"


def test_alignment_classifies_mapping_limited():
    rows = build_h4_d1_alignment_review([_inventory("NO_CONFIDENCE_MAPPING")], [_d1()])

    assert rows[0].h4_d1_alignment_class == "H4_D1_MAPPING_LIMITED"
