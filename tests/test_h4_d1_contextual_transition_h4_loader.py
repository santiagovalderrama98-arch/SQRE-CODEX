from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.h4_context_loader import load_h4_contexts


def test_h4_loader_reads_synthetic_combined_context_rows(tmp_path: Path):
    h4_dir = tmp_path / "h4"
    h4_dir.mkdir()
    (h4_dir / "h4_transition_state_context_interpretation_matrix.csv").write_text(
        "Context_ID,Scenario_ID,Source_State,Target_State,Transition_Label,Forward_Window,"
        "Combined_Context_Interpretation_Class,Combined_Context_Readiness_Flag,"
        "Combined_Dispersion_Class,Combined_Sensitivity_Class\n"
        "CTX_1,eurusd_h4_period_1,EXPANSION,CONSOLIDATION,EXPANSION -> CONSOLIDATION,12,"
        "CONTEXT_CONSISTENT_BUT_DISPERSED,REQUIRES_SCENARIO_LEVEL_INTERPRETATION,"
        "COMBINED_HIGH_DISPERSION,COMBINED_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )

    rows = load_h4_contexts(H4D1ContextualTransitionReviewConfig(h4_combined_context_dir=h4_dir))

    assert len(rows) == 1
    assert rows[0].h4_scenario_id == "eurusd_h4_period_1"
    assert rows[0].h4_combined_dispersion_class == "COMBINED_HIGH_DISPERSION"
