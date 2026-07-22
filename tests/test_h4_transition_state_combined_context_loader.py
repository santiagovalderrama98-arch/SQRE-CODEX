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
    config = H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=tmp_path / "empty_state_deep",
        h4_state_dispersion_dir=tmp_path / "empty_state_dispersion",
        h4_state_sensitive_dir=tmp_path / "empty_state_sensitive",
        h4_transition_deep_dive_dir=tmp_path / "empty_transition_deep",
        h4_transition_dispersion_dir=tmp_path / "empty_transition_dispersion",
        h4_transition_sensitive_dir=tmp_path / "empty_transition_sensitive",
        partial_complement_dir=tmp_path / "empty_partial_complement",
        partial_validation_dir=tmp_path / "empty_partial_validation",
        output_dir=tmp_path / "out",
    )

    rows = build_source_inventory(config)

    assert len(rows) == 13
    assert {row.source_type for row in rows} >= {"STATE_DEEP_DIVE", "TRANSITION_DEEP_DIVE", "PARTIAL_CONTEXT"}


def test_source_inventory_loads_state_sensitive_state_summary_alias(tmp_path: Path):
    sensitive_dir = tmp_path / "sensitive"
    sensitive_dir.mkdir()
    (sensitive_dir / "h4_scenario_sensitive_state_review_summary.csv").write_text(
        "H4_Scenario_Sensitive_Profile\nHIGH_SCENARIO_SENSITIVITY\n",
        encoding="utf-8",
    )
    config = H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=tmp_path / "empty_state_deep",
        h4_state_dispersion_dir=tmp_path / "empty_state_dispersion",
        h4_state_sensitive_dir=sensitive_dir,
        h4_transition_deep_dive_dir=tmp_path / "empty_transition_deep",
        h4_transition_dispersion_dir=tmp_path / "empty_transition_dispersion",
        h4_transition_sensitive_dir=tmp_path / "empty_transition_sensitive",
        partial_complement_dir=tmp_path / "empty_partial_complement",
        partial_validation_dir=tmp_path / "empty_partial_validation",
    )

    rows = build_source_inventory(config)
    state_sensitive = next(row for row in rows if row.source_name == "state_sensitive_summary")

    assert state_sensitive.load_status == "LOADED"
    assert state_sensitive.rows_loaded == 1
