from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.models import ScenarioBreakdownRow
from sqre.h4_transition_outcome_deep_dive.outcome_statistics import build_outcome_statistics, coefficient_of_variation


def test_outcome_statistics_compute_dispersion_and_safe_cv():
    rows = [
        ScenarioBreakdownRow("A -> B", "A", "B", "OTHER_TRANSITION_FAMILY", 3, "RESEARCH_READY", "S1", "H4", 10, 1, 1, 10, 8, 2, 4, 0.5, "N", "diag"),
        ScenarioBreakdownRow("A -> B", "A", "B", "OTHER_TRANSITION_FAMILY", 3, "RESEARCH_READY", "S2", "H4", 20, 3, 3, 20, 9, 2, 8, 0.7, "N", "diag"),
    ]

    stats = build_outcome_statistics(rows, H4TransitionOutcomeDeepDiveConfig())

    assert len(stats) == 1
    assert stats[0].total_sample_size == 30
    assert stats[0].forward_range_dispersion_pips == 10
    assert coefficient_of_variation(1, 0) == 0.0
