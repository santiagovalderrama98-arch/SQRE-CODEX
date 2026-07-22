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
    config = H4TransitionStateCombinedContextReviewConfig(h4_state_deep_dive_dir=state_dir)

    contexts = load_state_contexts(config)

    assert contexts[("EXPANSION", "12")].sample_size == 30
    assert contexts[("EXPANSION", "12")].sensitivity_status == "HIGH_SCENARIO_SENSITIVE"
