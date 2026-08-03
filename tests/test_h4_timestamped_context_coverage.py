from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.coverage_review import build_coverage_review
from sqre.h4_timestamped_context_table_generation.models import ScenarioInventoryRow, TimestampedContextRow


def _scenario(transitions: int) -> ScenarioInventoryRow:
    return ScenarioInventoryRow("SCN_1", "EURUSD", "H4", "", "", "", "COMPLETED", 0, transitions, True, True, 0, "", "")


def _context(context_id: str) -> TimestampedContextRow:
    return TimestampedContextRow(context_id, "CTX_1", "EURUSD", "H4", "SCN_1", "", "", "2026-01-01 04:00:00", "2026-01-01", "A", "B", "A -> B", "12", "EXACT_EVENT_TIMESTAMP", "2026-01-01", "TRANSITION_LABEL_FORWARD_WINDOW_MATCH", "HIGH_CONFIDENCE_CONTEXT_MATCH", "")


def test_coverage_review_classifies_full_coverage():
    rows = build_coverage_review([_scenario(2)], [_context("A"), _context("B")], H4TimestampedContextTableGenerationConfig())

    assert rows[0].coverage_class == "FULL_TEMPORAL_CONTEXT_COVERAGE"
    assert rows[0].coverage_ratio == 1.0


def test_coverage_review_classifies_missing_coverage():
    rows = build_coverage_review([_scenario(2)], [], H4TimestampedContextTableGenerationConfig())

    assert rows[0].coverage_class == "NO_TEMPORAL_CONTEXT_COVERAGE"
