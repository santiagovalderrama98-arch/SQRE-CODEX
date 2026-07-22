from pathlib import Path

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.loader import build_source_inventory, source_inventory_row


def test_source_inventory_reports_missing(tmp_path: Path):
    row = source_inventory_row("missing", "TEST", tmp_path / "missing.csv")

    assert row.load_status == "MISSING"
    assert row.rows_loaded == 0


def test_build_source_inventory_contains_expected_sources(tmp_path: Path):
    config = H4TransitionStateCombinedContextReviewConfig(output_dir=tmp_path / "out")

    rows = build_source_inventory(config)

    assert len(rows) == 13
    assert {row.source_type for row in rows} >= {"STATE_DEEP_DIVE", "TRANSITION_DEEP_DIVE", "PARTIAL_CONTEXT"}
