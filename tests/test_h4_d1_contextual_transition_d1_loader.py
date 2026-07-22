from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.d1_context_loader import load_d1_contexts


def test_d1_loader_reads_synthetic_regime_context_rows(tmp_path: Path):
    d1_dir = tmp_path / "d1"
    d1_dir.mkdir()
    (d1_dir / "d1_regime_outcome_review_summary.csv").write_text(
        "Scenario_ID,D1_Regime_Label,Condition_Label,Outcome_Dispersion_Class,Sample_Adequacy_Class\n"
        "eurusd_h4_period_1,TREND_REGIME,EXPANSION,HIGH_DISPERSION,SAMPLE_ADEQUATE\n",
        encoding="utf-8",
    )

    rows = load_d1_contexts(H4D1ContextualTransitionReviewConfig(d1_regime_outcome_review_dir=d1_dir))

    assert len(rows) == 1
    assert rows[0].d1_regime_label == "TREND_REGIME"
    assert rows[0].d1_dispersion_class == "HIGH_DISPERSION"
