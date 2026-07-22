from pathlib import Path

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.transition_context_loader import load_transition_contexts


def test_transition_loader_reads_transition_context_aliases(tmp_path: Path):
    transition_dir = tmp_path / "transition"
    transition_dir.mkdir()
    (transition_dir / "h4_transition_deep_dive_profile_inventory.csv").write_text(
        "Transition_Label,Forward_Window_Candles,Sample_Size,Sensitivity_Class\n"
        "EXPANSION -> CONSOLIDATION,12,42,HIGH_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )
    config = H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=tmp_path / "empty_state_deep",
        h4_state_dispersion_dir=tmp_path / "empty_state_dispersion",
        h4_state_sensitive_dir=tmp_path / "empty_state_sensitive",
        h4_transition_deep_dive_dir=transition_dir,
        h4_transition_dispersion_dir=tmp_path / "empty_transition_dispersion",
        h4_transition_sensitive_dir=tmp_path / "empty_transition_sensitive",
        partial_complement_dir=tmp_path / "empty_partial_complement",
        partial_validation_dir=tmp_path / "empty_partial_validation",
    )

    contexts = load_transition_contexts(config)

    assert len(contexts) == 1
    assert contexts[0].source_state == "EXPANSION"
    assert contexts[0].target_state == "CONSOLIDATION"
    assert contexts[0].sample_size == 42
