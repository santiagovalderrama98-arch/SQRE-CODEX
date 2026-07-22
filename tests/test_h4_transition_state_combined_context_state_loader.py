from pathlib import Path

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.state_context_loader import load_state_contexts


def test_state_loader_reads_state_context_aliases(tmp_path: Path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / "h4_state_deep_dive_profile_inventory.csv").write_text(
        "Condition_Value,Forward_Window_Candles,Sample_Size,Sensitivity_Class\n"
        "EXPANSION,12,30,HIGH_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )
    config = H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=state_dir,
        h4_state_dispersion_dir=tmp_path / "empty_state_dispersion",
        h4_state_sensitive_dir=tmp_path / "empty_state_sensitive",
        h4_transition_deep_dive_dir=tmp_path / "empty_transition_deep",
        h4_transition_dispersion_dir=tmp_path / "empty_transition_dispersion",
        h4_transition_sensitive_dir=tmp_path / "empty_transition_sensitive",
        partial_complement_dir=tmp_path / "empty_partial_complement",
        partial_validation_dir=tmp_path / "empty_partial_validation",
    )

    contexts = load_state_contexts(config)

    assert contexts[("EXPANSION", "12")].sample_size == 30
    assert contexts[("EXPANSION", "12")].sensitivity_status == "HIGH_SCENARIO_SENSITIVE"


def test_state_loader_reads_state_sensitive_summary_alias(tmp_path: Path):
    state_dir = tmp_path / "state"
    sensitive_dir = tmp_path / "sensitive"
    state_dir.mkdir()
    sensitive_dir.mkdir()
    (state_dir / "h4_state_deep_dive_profile_inventory.csv").write_text(
        "Condition_Value,Forward_Window_Candles\nEXPANSION,12\n",
        encoding="utf-8",
    )
    (sensitive_dir / "h4_scenario_sensitive_state_review_summary.csv").write_text(
        "H4_Scenario_Sensitive_Profile,H4_Review_Readiness_Flag\n"
        "HIGH_SCENARIO_SENSITIVITY,H4_REQUIRES_SCENARIO_LEVEL_REVIEW\n",
        encoding="utf-8",
    )
    config = H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=state_dir,
        h4_state_dispersion_dir=tmp_path / "empty_state_dispersion",
        h4_state_sensitive_dir=sensitive_dir,
        h4_transition_deep_dive_dir=tmp_path / "empty_transition_deep",
        h4_transition_dispersion_dir=tmp_path / "empty_transition_dispersion",
        h4_transition_sensitive_dir=tmp_path / "empty_transition_sensitive",
        partial_complement_dir=tmp_path / "empty_partial_complement",
        partial_validation_dir=tmp_path / "empty_partial_validation",
    )

    contexts = load_state_contexts(config)

    assert contexts[("EXPANSION", "12")].sensitivity_status == "HIGH_SCENARIO_SENSITIVITY"
