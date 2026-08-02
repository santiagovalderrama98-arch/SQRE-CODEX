from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.d1_regime_context_review import (
    build_d1_regime_context_review,
    build_h4_d1_context_inventory,
)
from sqre.h4_d1_contextual_transition_review.models import D1ContextRow, H4ContextRow, H4D1ContextInventoryRow
from sqre.h4_d1_contextual_transition_review.scenario_context_mapper import build_scenario_context_map


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


def test_context_inventory_marks_condition_level_match_available():
    h4 = H4ContextRow(
        "CTX_1",
        "EURUSD",
        "EXPANSION",
        "CONSOLIDATION",
        "EXPANSION -> CONSOLIDATION",
        "12",
        "CONTEXT_INPUT_LIMITED",
        "LIMITED",
        "COMBINED_HIGH_DISPERSION",
        "COMBINED_SCENARIO_SENSITIVE",
    )
    d1 = [
        D1ContextRow(
            "D1_1",
            "",
            "TREND_REGIME",
            "EXPANSION -> CONSOLIDATION",
            "PROFILE",
            "HIGH_DISPERSION",
            "SAMPLE_ADEQUATE",
            "READY",
            d1_condition_type="TRANSITION",
            d1_forward_window="12",
            d1_context_status="D1_CONTEXT_AVAILABLE_CONDITION_LEVEL",
            d1_sensitivity_class="REGIME_SENSITIVE",
        )
    ]
    mapping = build_scenario_context_map([h4], d1, H4D1ContextualTransitionReviewConfig())

    rows = build_h4_d1_context_inventory([h4], d1, mapping, "PARTIAL_CONTEXT_UNAVAILABLE", H4D1ContextualTransitionReviewConfig())

    assert rows[0].d1_context_status == "D1_CONTEXT_AVAILABLE_CONDITION_LEVEL"
    assert rows[0].d1_regime_label == "TREND_REGIME"
    assert "no scenario/date alignment inferred" in rows[0].context_inventory_diagnostic
