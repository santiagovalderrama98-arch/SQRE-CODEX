from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.models import D1ContextRow, H4ContextRow
from sqre.h4_d1_contextual_transition_review.scenario_context_mapper import build_scenario_context_map


def _h4(scenario_id: str) -> H4ContextRow:
    return H4ContextRow("CTX_1", "EURUSD", "A", "B", "A -> B", "12", "CONTEXT_INPUT_LIMITED", "LIMITED", "HIGH", "HIGH", scenario_id)


def test_scenario_mapper_handles_explicit_scenario_id_mapping():
    d1 = [D1ContextRow("D1_1", "eurusd_h4_period_1", "TREND_REGIME", "TREND", "PROFILE", "HIGH", "OK", "OK")]

    rows = build_scenario_context_map([_h4("eurusd_h4_period_1")], d1, H4D1ContextualTransitionReviewConfig())

    assert rows[0].mapping_method == "EXPLICIT_SCENARIO_ID"
    assert rows[0].mapping_confidence_class == "HIGH_CONFIDENCE_MAPPING"


def test_scenario_mapper_handles_unmapped_contexts_safely():
    rows = build_scenario_context_map([_h4("")], [], H4D1ContextualTransitionReviewConfig())

    assert rows[0].mapping_method == "UNMAPPED"
    assert rows[0].mapping_confidence_class == "NO_CONFIDENCE_MAPPING"
