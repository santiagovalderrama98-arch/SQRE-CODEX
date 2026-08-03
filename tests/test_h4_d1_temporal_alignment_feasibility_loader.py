from pathlib import Path

from sqre.h4_d1_temporal_alignment_feasibility_review.config import H4D1TemporalAlignmentFeasibilityConfig
from sqre.h4_d1_temporal_alignment_feasibility_review.source_inventory import build_source_inventory


def test_loader_handles_missing_optional_inputs_safely(tmp_path: Path):
    config = H4D1TemporalAlignmentFeasibilityConfig(
        h4_combined_context_dir=tmp_path / "missing_h4",
        h4_d1_structural_research_dir=tmp_path / "missing_structural",
        h4_d1_validation_dir=tmp_path / "missing_validation",
        d1_regime_normalized_dir=tmp_path / "missing_d1_normalized",
        d1_regime_outcome_review_dir=tmp_path / "missing_d1_outcome",
        d1_state_deep_dive_dir=tmp_path / "missing_d1_state",
    )

    rows = build_source_inventory(config)

    assert rows
    assert all(row.load_status == "MISSING" for row in rows)
    assert all(row.rows_loaded == 0 for row in rows)
