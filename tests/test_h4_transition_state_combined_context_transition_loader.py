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
    config = H4TransitionStateCombinedContextReviewConfig(h4_transition_deep_dive_dir=transition_dir)

    contexts = load_transition_contexts(config)

    assert contexts[0].source_state == "EXPANSION"
    assert contexts[0].target_state == "CONSOLIDATION"
    assert contexts[0].sample_size == 42
