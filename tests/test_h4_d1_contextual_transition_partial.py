from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.models import H4D1ContextInventoryRow
from sqre.h4_d1_contextual_transition_review.partial_context_integrator import build_partial_context_integration


def test_partial_integration_classifies_limited_complement(tmp_path: Path):
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    (partial_dir / "h4_partial_complementary_dispersion_summary.csv").write_text(
        "Dominant_Partial_Baseline_Interpretation,H4_Partial_Complementary_Readiness_Flag\n"
        "PARTIAL_CONTEXT_CONSISTENT_BUT_LIMITED,PARTIAL_CONTEXT_REQUIRES_LIMITED_INTERPRETATION\n",
        encoding="utf-8",
    )
    inventory = H4D1ContextInventoryRow(
        "CTX_1", "EURUSD", "H4", "D1", "A", "B", "A -> B", "12", "CONTEXT", "READY",
        "HIGH", "HIGH", "TREND_REGIME", "D1_CONTEXT_AVAILABLE", "OK", "HIGH",
        "PARTIAL_CONTEXT_AVAILABLE", "HIGH_CONFIDENCE_MAPPING", "ok",
    )

    rows = build_partial_context_integration(
        [inventory],
        H4D1ContextualTransitionReviewConfig(partial_complement_dir=partial_dir),
    )

    assert rows[0].h4_d1_partial_use_class == "PARTIAL_CONTEXT_LIMITED_COMPLEMENT"
