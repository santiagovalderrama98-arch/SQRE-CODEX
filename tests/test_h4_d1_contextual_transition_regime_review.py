from sqre.h4_d1_contextual_transition_review.d1_regime_context_review import build_d1_regime_context_review
from sqre.h4_d1_contextual_transition_review.models import D1ContextRow, H4D1ContextInventoryRow


def _inventory(dispersion: str, sample: str) -> H4D1ContextInventoryRow:
    return H4D1ContextInventoryRow(
        "CTX_1", "EURUSD", "H4", "D1", "A", "B", "A -> B", "12", "CONTEXT", "READY",
        "HIGH", "HIGH", "TREND_REGIME", "D1_CONTEXT_AVAILABLE", sample, dispersion,
        "PARTIAL_CONTEXT_UNAVAILABLE", "HIGH_CONFIDENCE_MAPPING", "ok",
    )


def test_regime_review_classifies_regime_sensitive():
    rows = build_d1_regime_context_review([_inventory("HIGH_DISPERSION", "SAMPLE_ADEQUATE")], [])

    assert rows[0].d1_context_interpretation_class == "D1_CONTEXT_REGIME_SENSITIVE"


def test_regime_review_classifies_sample_constrained():
    rows = build_d1_regime_context_review([_inventory("MODERATE_DISPERSION", "LOW_SAMPLE_SIZE")], [])

    assert rows[0].d1_context_interpretation_class == "D1_CONTEXT_SAMPLE_CONSTRAINED"
