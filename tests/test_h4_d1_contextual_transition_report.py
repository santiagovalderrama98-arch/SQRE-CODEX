from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.h4_d1_contextual_transition_review_pipeline import (
    run_h4_d1_contextual_transition_review,
)
from sqre.h4_d1_contextual_transition_review.reports import FORBIDDEN_REPORT_TERMS


def test_report_includes_required_sections_and_excludes_forbidden_language(tmp_path: Path):
    config = H4D1ContextualTransitionReviewConfig(
        h4_combined_context_dir=tmp_path / "missing_h4",
        d1_regime_normalized_dir=tmp_path / "missing_d1_regime",
        d1_regime_outcome_review_dir=tmp_path / "missing_d1_outcome",
        d1_state_deep_dive_dir=tmp_path / "missing_d1_state",
        h4_d1_structural_research_dir=tmp_path / "missing_structural",
        h4_d1_validation_dir=tmp_path / "missing_validation",
        partial_complement_dir=tmp_path / "missing_partial",
        partial_validation_dir=tmp_path / "missing_partial_validation",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )

    result = run_h4_d1_contextual_transition_review(config)
    text = result.report_path.read_text(encoding="utf-8")

    assert "H4/D1 Scenario Context Map" in text
    assert "Contextual Dispersion Review" in text
    assert "Do Not Change Yet" in text
    assert all(term not in text.lower() for term in FORBIDDEN_REPORT_TERMS)


def test_report_includes_sample_adequacy_diagnostic_for_condition_level_mapping(tmp_path: Path):
    h4_dir = tmp_path / "h4"
    d1_dir = tmp_path / "d1"
    h4_dir.mkdir()
    d1_dir.mkdir()
    (h4_dir / "h4_transition_state_context_interpretation_matrix.csv").write_text(
        "Context_ID,Source_State,Target_State,Transition_Label,Forward_Window,"
        "Combined_Context_Interpretation_Class,Combined_Context_Readiness_Flag,"
        "Combined_Dispersion_Class,Combined_Sensitivity_Class\n"
        "CTX_1,EXPANSION,CONSOLIDATION,EXPANSION -> CONSOLIDATION,12,"
        "CONTEXT_CONSISTENT_BUT_DISPERSED,REQUIRES_SCENARIO_LEVEL_INTERPRETATION,"
        "COMBINED_HIGH_DISPERSION,COMBINED_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )
    (d1_dir / "d1_condition_quality_inventory.csv").write_text(
        "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Regimes_Present,"
        "Dispersion_Class,Sensitivity_Class,Sample_Adequacy_Class\n"
        "TRANSITION,EXPANSION -> CONSOLIDATION,12,2,TREND|RANGE,MODERATE_DISPERSION,"
        "STABLE,LOW_SAMPLE_SIZE\n",
        encoding="utf-8",
    )
    config = H4D1ContextualTransitionReviewConfig(
        h4_combined_context_dir=h4_dir,
        d1_regime_normalized_dir=tmp_path / "missing_d1_regime",
        d1_regime_outcome_review_dir=d1_dir,
        d1_state_deep_dive_dir=tmp_path / "missing_d1_state",
        h4_d1_structural_research_dir=tmp_path / "missing_structural",
        h4_d1_validation_dir=tmp_path / "missing_validation",
        partial_complement_dir=tmp_path / "missing_partial",
        partial_validation_dir=tmp_path / "missing_partial_validation",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )

    result = run_h4_d1_contextual_transition_review(config)
    text = result.report_path.read_text(encoding="utf-8")

    assert result.summary is not None
    assert result.summary.h4_d1_contextual_readiness_flag == "H4_D1_REQUIRES_SAMPLE_ADEQUACY_REVIEW"
    assert "H4/D1 context is dominated by D1 sample adequacy constraints" in text
    assert "condition-level mapping remains descriptive and does not infer scenario/date alignment" in text
    assert "Mapped by condition label and forward window; no scenario/date alignment inferred." in text
    assert all(term not in text.lower() for term in FORBIDDEN_REPORT_TERMS)
