from sqre.h4_d1_contextual_transition_review.contextual_interpretation import build_contextual_interpretation_matrix
from sqre.h4_d1_contextual_transition_review.models import (
    ContextualDispersionReviewRow,
    ContextualSensitivityReviewRow,
    H4D1AlignmentReviewRow,
    H4D1ContextInventoryRow,
    PartialContextIntegrationRow,
)


def _inventory() -> H4D1ContextInventoryRow:
    return H4D1ContextInventoryRow(
        "CTX_1", "EURUSD", "H4", "D1", "A", "B", "A -> B", "12", "CONTEXT", "READY",
        "HIGH", "HIGH", "TREND_REGIME", "D1_CONTEXT_AVAILABLE", "OK", "HIGH",
        "PARTIAL_CONTEXT_AVAILABLE", "HIGH_CONFIDENCE_MAPPING", "ok",
    )


def test_interpretation_classifies_scenario_regime_level_interpretation():
    alignment = H4D1AlignmentReviewRow("CTX_1", "A", "B", "A -> B", "12", "CONTEXT", "READY", "D1_CONTEXT_REGIME_SENSITIVE", "TREND_REGIME", "H4_D1_ALIGNED_SCENARIO_AND_REGIME_SENSITIVE", "ok")
    dispersion = ContextualDispersionReviewRow("CTX_1", "A -> B", "12", "HIGH", "HIGH", "TREND", "D1_CONTEXT_REINFORCES_H4_DISPERSION", "MIXED_H4_D1_DRIVEN", "ok")
    sensitivity = ContextualSensitivityReviewRow("CTX_1", "HIGH", "D1_REGIME_SENSITIVE", "TREND", "D1_REINFORCES_H4_SCENARIO_SENSITIVITY", "ok")
    partial = PartialContextIntegrationRow("CTX_1", "P1", "PARTIAL_SAMPLE", "LIMITED", "LIMITED", "LIMITED", "PARTIAL_CONTEXT_LIMITED_COMPLEMENT", "ok")

    rows = build_contextual_interpretation_matrix([_inventory()], [alignment], [dispersion], [sensitivity], [partial])

    assert rows[0].h4_d1_contextual_interpretation_class == "D1_CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION"


def test_interpretation_classifies_input_limited():
    alignment = H4D1AlignmentReviewRow("CTX_1", "A", "B", "A -> B", "12", "CONTEXT", "READY", "D1_CONTEXT_UNAVAILABLE", "D1_CONTEXT_UNMAPPED", "H4_D1_MAPPING_LIMITED", "missing")
    dispersion = ContextualDispersionReviewRow("CTX_1", "A -> B", "12", "NA", "NA", "NA", "D1_CONTEXT_INPUT_LIMITED", "INPUT_LIMITED", "missing")
    sensitivity = ContextualSensitivityReviewRow("CTX_1", "NA", "NA", "NA", "D1_CONTEXT_INPUT_LIMITED", "missing")
    partial = PartialContextIntegrationRow("CTX_1", "P1", "PARTIAL_SAMPLE", "NA", "NA", "NA", "PARTIAL_CONTEXT_UNAVAILABLE", "missing")

    rows = build_contextual_interpretation_matrix([_inventory()], [alignment], [dispersion], [sensitivity], [partial])

    assert rows[0].h4_d1_contextual_interpretation_class == "D1_CONTEXT_INPUT_LIMITED"
