from pathlib import Path

from sqre.h4_transition_state_combined_context_review.config import H4TransitionStateCombinedContextReviewConfig
from sqre.h4_transition_state_combined_context_review.h4_transition_state_combined_context_review_pipeline import (
    run_h4_transition_state_combined_context_review,
)


def test_report_writes_required_sections(tmp_path: Path):
    config = _fixture_config(tmp_path)
    _write_minimal_inputs(config)

    result = run_h4_transition_state_combined_context_review(config)
    text = result.report_path.read_text(encoding="utf-8")

    assert "SQRE H4 Transition/State Combined Context Review" in text
    assert "Combined Context Interpretation Matrix" in text
    assert "No production defaults were modified." in text
    assert (config.output_dir / "h4_transition_state_combined_context_summary.csv").exists()


def _fixture_config(tmp_path: Path) -> H4TransitionStateCombinedContextReviewConfig:
    return H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=tmp_path / "state_deep",
        h4_state_dispersion_dir=tmp_path / "state_dispersion",
        h4_state_sensitive_dir=tmp_path / "state_sensitive",
        h4_transition_deep_dive_dir=tmp_path / "transition_deep",
        h4_transition_dispersion_dir=tmp_path / "transition_dispersion",
        h4_transition_sensitive_dir=tmp_path / "transition_sensitive",
        partial_complement_dir=tmp_path / "partial",
        partial_validation_dir=tmp_path / "partial_validation",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )


def _write_minimal_inputs(config: H4TransitionStateCombinedContextReviewConfig) -> None:
    for directory in [
        config.h4_state_deep_dive_dir,
        config.h4_state_dispersion_dir,
        config.h4_state_sensitive_dir,
        config.h4_transition_deep_dive_dir,
        config.h4_transition_sensitive_dir,
        config.partial_complement_dir,
    ]:
        directory.mkdir(parents=True)
    (config.h4_state_deep_dive_dir / "h4_state_deep_dive_profile_inventory.csv").write_text(
        "Condition_Value,Forward_Window_Candles,Sensitivity_Class\nEXPANSION,12,HIGH_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )
    (config.h4_transition_deep_dive_dir / "h4_transition_deep_dive_profile_inventory.csv").write_text(
        "Transition_Label,Forward_Window_Candles,Sensitivity_Class\nEXPANSION -> CONSOLIDATION,12,HIGH_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )
    (config.partial_complement_dir / "h4_partial_baseline_interpretation_matrix.csv").write_text(
        "Candidate_ID,Sample_Label,Partial_Baseline_Interpretation_Class\n"
        "P1,PARTIAL_SAMPLE,COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED\n",
        encoding="utf-8",
    )
    (config.partial_complement_dir / "h4_partial_complementary_dispersion_summary.csv").write_text(
        "H4_Partial_Complementary_Readiness_Flag\nPARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION\n",
        encoding="utf-8",
    )
