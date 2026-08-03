from pathlib import Path

from sqre.h4_d1_temporal_alignment_feasibility_review.config import H4D1TemporalAlignmentFeasibilityConfig
from sqre.h4_d1_temporal_alignment_feasibility_review.h4_d1_temporal_alignment_feasibility_pipeline import (
    run_h4_d1_temporal_alignment_feasibility_review,
)
from sqre.h4_d1_temporal_alignment_feasibility_review.reports import FORBIDDEN_REPORT_TERMS


def test_report_includes_required_sections_and_excludes_forbidden_language(tmp_path: Path):
    config = _condition_only_config(tmp_path)

    result = run_h4_d1_temporal_alignment_feasibility_review(config)
    text = result.report_path.read_text(encoding="utf-8")

    assert "SQRE H4/D1 Temporal Alignment Feasibility Review" in text
    assert "Temporal Key Inventory" in text
    assert "Alignment Candidate Review" in text
    assert "Missing Temporal Keys Review" in text
    assert "Research Readiness Assessment" in text
    assert "This review checks feasibility only." in text
    assert "does not use condition-level matching as same-time alignment" in text
    assert "Same-time H4/D1 alignment requires timestamp, interval, or scenario-period keys." in text
    assert all(term not in text.lower() for term in FORBIDDEN_REPORT_TERMS)


def _condition_only_config(tmp_path: Path) -> H4D1TemporalAlignmentFeasibilityConfig:
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
        "Condition_Label,Forward_Window,Regime_Label\nEXPANSION -> CONSOLIDATION,12,TREND\n",
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
