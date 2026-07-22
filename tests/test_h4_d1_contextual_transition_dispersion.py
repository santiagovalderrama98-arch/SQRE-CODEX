from sqre.h4_d1_contextual_transition_review.contextual_dispersion_review import build_contextual_dispersion_review
from sqre.h4_d1_contextual_transition_review.models import D1RegimeContextReviewRow, H4D1ContextInventoryRow


def _inventory(status: str = "D1_CONTEXT_AVAILABLE") -> H4D1ContextInventoryRow:
    return H4D1ContextInventoryRow(
        "CTX_1", "EURUSD", "H4", "D1", "A", "B", "A -> B", "12", "CONTEXT", "READY",
        "COMBINED_HIGH_DISPERSION", "HIGH", "TREND_REGIME", status, "SAMPLE_ADEQUATE",
        "HIGH_DISPERSION", "PARTIAL_CONTEXT_UNAVAILABLE", "HIGH_CONFIDENCE_MAPPING", "ok",
    )


def test_contextual_dispersion_classifies_d1_reinforcing_h4_dispersion():
    d1 = D1RegimeContextReviewRow("CTX_1", "TREND_REGIME", "D1_CONTEXT_AVAILABLE", 1, "OK", "HIGH_DISPERSION", "D1_REGIME_SENSITIVE", "D1_CONTEXT_REGIME_SENSITIVE", "ok")

    rows = build_contextual_dispersion_review([_inventory()], [d1])

    assert rows[0].contextual_dispersion_class == "D1_CONTEXT_REINFORCES_H4_DISPERSION"


def test_contextual_dispersion_classifies_input_limited():
    d1 = D1RegimeContextReviewRow("CTX_1", "D1_CONTEXT_UNMAPPED", "D1_CONTEXT_UNAVAILABLE", 0, "NA", "NA", "NA", "D1_CONTEXT_UNAVAILABLE", "missing")

    rows = build_contextual_dispersion_review([_inventory("D1_CONTEXT_UNAVAILABLE")], [d1])

    assert rows[0].contextual_dispersion_class == "D1_CONTEXT_INPUT_LIMITED"
