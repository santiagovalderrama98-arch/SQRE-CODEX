from sqre.h4_transition_outcome_deep_dive.comparative_review import build_scenario_comparison_matrix
from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.models import OutcomeStatisticsRow, ScenarioBreakdownRow


def test_comparative_review_computes_scenario_deviation_classes():
    breakdown = [
        ScenarioBreakdownRow("A -> B", "A", "B", "OTHER_TRANSITION_FAMILY", 3, "RESEARCH_READY", "S1", "H4", 10, 1, 1, 30, 8, 2, 30, 1.0, "N", "diag")
    ]
    stats = [
        OutcomeStatisticsRow("A -> B", "A", "B", "OTHER_TRANSITION_FAMILY", 3, "RESEARCH_READY", 1, 10, 10, 1, 1, 1, 0, 10, 10, 10, 0, 0, 10, 10, 10, 0, 0, 0.5, 0.5, 0.5, 0, "STABLE_DESCRIPTIVE", "diag", "follow")
    ]

    comparisons = build_scenario_comparison_matrix(breakdown, stats, H4TransitionOutcomeDeepDiveConfig())

    assert comparisons[0].scenario_deviation_class == "HIGH_DEVIATION"
