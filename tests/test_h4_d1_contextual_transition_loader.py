from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.loader import build_source_inventory, read_optional_csv


def test_loader_handles_missing_optional_inputs(tmp_path: Path):
    config = H4D1ContextualTransitionReviewConfig(
        h4_combined_context_dir=tmp_path / "missing_h4",
        d1_regime_normalized_dir=tmp_path / "missing_d1_regime",
        d1_regime_outcome_review_dir=tmp_path / "missing_d1_outcome",
        d1_state_deep_dive_dir=tmp_path / "missing_d1_state",
        h4_d1_structural_research_dir=tmp_path / "missing_structural",
        h4_d1_validation_dir=tmp_path / "missing_validation",
        partial_complement_dir=tmp_path / "missing_partial",
        partial_validation_dir=tmp_path / "missing_partial_validation",
    )

    inventory = build_source_inventory(config)

    assert read_optional_csv(tmp_path / "missing.csv").empty
    assert len(inventory) == 10
    assert {row.load_status for row in inventory} == {"MISSING"}
