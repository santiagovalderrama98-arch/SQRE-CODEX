from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.d1_context_loader import load_d1_contexts


def _isolated_config(tmp_path: Path, **overrides) -> H4D1ContextualTransitionReviewConfig:
    values = {
        "h4_combined_context_dir": tmp_path / "empty_h4",
        "d1_regime_normalized_dir": tmp_path / "empty_d1_normalized",
        "d1_regime_outcome_review_dir": tmp_path / "empty_d1_outcome",
        "d1_state_deep_dive_dir": tmp_path / "empty_d1_state",
        "h4_d1_structural_research_dir": tmp_path / "empty_h4_d1_research",
        "h4_d1_validation_dir": tmp_path / "empty_h4_d1_validation",
        "partial_complement_dir": tmp_path / "empty_partial",
        "partial_validation_dir": tmp_path / "empty_partial_validation",
    }
    values.update(overrides)
    return H4D1ContextualTransitionReviewConfig(**values)


def test_d1_loader_reads_synthetic_regime_context_rows(tmp_path: Path):
    d1_dir = tmp_path / "d1"
    d1_dir.mkdir()
    (d1_dir / "d1_regime_outcome_review_summary.csv").write_text(
        "Scenario_ID,D1_Regime_Label,Condition_Label,Outcome_Dispersion_Class,Sample_Adequacy_Class\n"
        "eurusd_h4_period_1,TREND_REGIME,EXPANSION,HIGH_DISPERSION,SAMPLE_ADEQUATE\n",
        encoding="utf-8",
    )

    config = _isolated_config(tmp_path, d1_regime_outcome_review_dir=d1_dir)

    rows = load_d1_contexts(config)

    assert len(rows) == 1
    assert rows[0].d1_regime_label == "TREND_REGIME"
    assert rows[0].d1_dispersion_class == "HIGH_DISPERSION"


def test_d1_loader_reads_condition_profile_evidence(tmp_path: Path):
    d1_dir = tmp_path / "d1_outcome"
    d1_dir.mkdir()
    (d1_dir / "d1_condition_quality_inventory.csv").write_text(
        "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Regimes_Present,"
        "Dispersion_Class,Sensitivity_Class,Sample_Adequacy_Class\n"
        "TRANSITION,EXPANSION -> CONSOLIDATION,12,2,TREND|RANGE,HIGH_DISPERSION,"
        "REGIME_SENSITIVE,SAMPLE_ADEQUATE\n",
        encoding="utf-8",
    )

    rows = load_d1_contexts(_isolated_config(tmp_path, d1_regime_outcome_review_dir=d1_dir))

    assert len(rows) == 1
    assert rows[0].d1_context_status == "D1_CONTEXT_AVAILABLE_CONDITION_LEVEL"
    assert rows[0].d1_condition_type == "TRANSITION"
    assert rows[0].d1_forward_window == "12"
    assert rows[0].d1_regime_label == "MULTI_REGIME:RANGE|TREND"


def test_d1_loader_reads_structural_and_validation_summary_aliases(tmp_path: Path):
    structural_dir = tmp_path / "structural"
    validation_dir = tmp_path / "validation"
    structural_dir.mkdir()
    validation_dir.mkdir()
    (structural_dir / "h4_d1_timeframe_research_summary.csv").write_text(
        "Scenario_ID,D1_Regime_Label,Condition_Label,Outcome_Dispersion_Class\n"
        "eurusd_h4_period_1,TREND_REGIME,STRUCTURAL_CONTEXT,MODERATE_DISPERSION\n",
        encoding="utf-8",
    )
    (validation_dir / "h4_d1_validation_summary.csv").write_text(
        "Scenario_ID,D1_Regime_Label,Condition_Label,Outcome_Dispersion_Class\n"
        "eurusd_d1_period_1,RANGE_REGIME,VALIDATION_CONTEXT,LOW_DISPERSION\n",
        encoding="utf-8",
    )

    rows = load_d1_contexts(
        _isolated_config(
            tmp_path,
            h4_d1_structural_research_dir=structural_dir,
            h4_d1_validation_dir=validation_dir,
        )
    )

    assert {row.d1_context_label for row in rows} == {"STRUCTURAL_CONTEXT", "VALIDATION_CONTEXT"}
    assert all(row.d1_context_status == "D1_CONTEXT_AVAILABLE_SUMMARY_LEVEL" for row in rows)
