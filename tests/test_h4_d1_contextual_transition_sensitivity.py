from sqre.h4_d1_contextual_transition_review.contextual_sensitivity_review import build_contextual_sensitivity_review
from sqre.h4_d1_contextual_transition_review.models import D1RegimeContextReviewRow, H4D1ContextInventoryRow


def test_contextual_sensitivity_classifies_d1_reinforcing_h4_scenario_sensitivity():
    inventory = H4D1ContextInventoryRow(
        "CTX_1", "EURUSD", "H4", "D1", "A", "B", "A -> B", "12", "CONTEXT", "READY",
        "HIGH", "COMBINED_SCENARIO_SENSITIVE", "TREND_REGIME", "D1_CONTEXT_AVAILABLE",
        "OK", "HIGH", "PARTIAL_CONTEXT_UNAVAILABLE", "HIGH_CONFIDENCE_MAPPING", "ok",
    )
    d1 = D1RegimeContextReviewRow("CTX_1", "TREND_REGIME", "D1_CONTEXT_AVAILABLE", 1, "OK", "HIGH", "D1_REGIME_SENSITIVE", "D1_CONTEXT_REGIME_SENSITIVE", "ok")

    rows = build_contextual_sensitivity_review([inventory], [d1])

    assert rows[0].contextual_sensitivity_class == "D1_REINFORCES_H4_SCENARIO_SENSITIVITY"
