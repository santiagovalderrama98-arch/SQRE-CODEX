from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.h4_d1_contextual_transition_review_pipeline import (
    run_h4_d1_contextual_transition_review,
)


def _write_synthetic_inputs(tmp_path: Path) -> H4D1ContextualTransitionReviewConfig:
    h4_dir = tmp_path / "h4"
    d1_dir = tmp_path / "d1"
    partial_dir = tmp_path / "partial"
    h4_dir.mkdir()
    d1_dir.mkdir()
    partial_dir.mkdir()
    (h4_dir / "h4_transition_state_context_interpretation_matrix.csv").write_text(
        "Context_ID,Scenario_ID,Source_State,Target_State,Transition_Label,Forward_Window,"
        "Combined_Context_Interpretation_Class,Combined_Context_Readiness_Flag,"
        "Combined_Dispersion_Class,Combined_Sensitivity_Class\n"
        "CTX_1,eurusd_h4_period_1,EXPANSION,CONSOLIDATION,EXPANSION -> CONSOLIDATION,12,"
        "CONTEXT_CONSISTENT_BUT_DISPERSED,REQUIRES_SCENARIO_LEVEL_INTERPRETATION,"
        "COMBINED_HIGH_DISPERSION,COMBINED_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )
    (d1_dir / "d1_regime_outcome_review_summary.csv").write_text(
        "Scenario_ID,D1_Regime_Label,Condition_Label,Outcome_Dispersion_Class,Sample_Adequacy_Class\n"
        "eurusd_h4_period_1,TREND_REGIME,EXPANSION,HIGH_DISPERSION,SAMPLE_ADEQUATE\n",
        encoding="utf-8",
    )
    (partial_dir / "h4_partial_complementary_dispersion_summary.csv").write_text(
        "Dominant_Partial_Baseline_Interpretation,H4_Partial_Complementary_Readiness_Flag\n"
        "PARTIAL_CONTEXT_CONSISTENT_BUT_LIMITED,PARTIAL_CONTEXT_REQUIRES_LIMITED_INTERPRETATION\n",
        encoding="utf-8",
    )
    return H4D1ContextualTransitionReviewConfig(
        h4_combined_context_dir=h4_dir,
        d1_regime_outcome_review_dir=d1_dir,
        d1_regime_normalized_dir=tmp_path / "missing_regime",
        d1_state_deep_dive_dir=tmp_path / "missing_state",
        h4_d1_structural_research_dir=tmp_path / "missing_structural",
        h4_d1_validation_dir=tmp_path / "missing_validation",
        partial_complement_dir=partial_dir,
        partial_validation_dir=tmp_path / "missing_partial_validation",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )


def test_pipeline_writes_all_expected_outputs(tmp_path: Path):
    config = _write_synthetic_inputs(tmp_path)

    result = run_h4_d1_contextual_transition_review(config)

    expected = [
        "h4_d1_context_source_inventory.csv",
        "h4_d1_scenario_context_map.csv",
        "h4_d1_context_inventory.csv",
        "h4_d1_regime_context_review.csv",
        "h4_d1_alignment_review.csv",
        "h4_d1_contextual_dispersion_review.csv",
        "h4_d1_contextual_sensitivity_review.csv",
        "h4_d1_partial_context_integration.csv",
        "h4_d1_contextual_interpretation_matrix.csv",
        "h4_d1_contextual_transition_summary.csv",
    ]
    assert all((config.output_dir / filename).exists() for filename in expected)
    assert result.report_path.exists()
    assert result.summary is not None
