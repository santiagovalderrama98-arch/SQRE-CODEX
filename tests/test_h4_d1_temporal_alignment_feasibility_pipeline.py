from pathlib import Path

from sqre.h4_d1_temporal_alignment_feasibility_review.config import H4D1TemporalAlignmentFeasibilityConfig
from sqre.h4_d1_temporal_alignment_feasibility_review.h4_d1_temporal_alignment_feasibility_pipeline import (
    run_h4_d1_temporal_alignment_feasibility_review,
)


def test_pipeline_writes_all_expected_outputs(tmp_path: Path):
    config = _config_with_condition_only_sources(tmp_path)

    result = run_h4_d1_temporal_alignment_feasibility_review(config)

    expected = [
        "h4_d1_temporal_source_inventory.csv",
        "h4_d1_temporal_key_inventory.csv",
        "h4_d1_temporal_alignment_candidate_review.csv",
        "h4_d1_missing_temporal_keys_review.csv",
        "h4_d1_temporal_alignment_feasibility_summary.csv",
    ]
    assert all((config.output_dir / filename).exists() for filename in expected)
    assert result.report_path.exists()
    assert result.summary is not None
    assert result.summary.temporal_alignment_readiness_flag == "CONDITION_LEVEL_ONLY_NOT_TEMPORAL_ALIGNMENT"


def _config_with_condition_only_sources(tmp_path: Path) -> H4D1TemporalAlignmentFeasibilityConfig:
    h4_dir = tmp_path / "h4"
    d1_dir = tmp_path / "d1"
    h4_dir.mkdir()
    d1_dir.mkdir()
    (h4_dir / "h4_transition_state_context_interpretation_matrix.csv").write_text(
        "Context_ID,Source_State,Target_State,Transition_Label,Forward_Window\n"
        "CTX_1,EXPANSION,CONSOLIDATION,EXPANSION -> CONSOLIDATION,12\n",
        encoding="utf-8",
    )
    (d1_dir / "d1_condition_quality_inventory.csv").write_text(
        "Condition_Label,Forward_Window\nEXPANSION -> CONSOLIDATION,12\n",
        encoding="utf-8",
    )
    return H4D1TemporalAlignmentFeasibilityConfig(
        h4_combined_context_dir=h4_dir,
        d1_regime_outcome_review_dir=d1_dir,
        h4_d1_structural_research_dir=tmp_path / "missing_structural",
        h4_d1_validation_dir=tmp_path / "missing_validation",
        d1_regime_normalized_dir=tmp_path / "missing_d1_normalized",
        d1_state_deep_dive_dir=tmp_path / "missing_d1_state",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )
