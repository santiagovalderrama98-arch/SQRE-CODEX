from pathlib import Path

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.partial_context_loader import load_partial_context


def test_partial_loader_reads_partial_summary(tmp_path: Path):
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    (partial_dir / "h4_partial_baseline_interpretation_matrix.csv").write_text(
        "Candidate_ID,Sample_Label,Partial_Baseline_Interpretation_Class\n"
        "P1,PARTIAL_SAMPLE,COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED\n",
        encoding="utf-8",
    )
    (partial_dir / "h4_partial_complementary_dispersion_summary.csv").write_text(
        "H4_Partial_Complementary_Readiness_Flag\nPARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION\n",
        encoding="utf-8",
    )
    config = H4TransitionStateCombinedContextReviewConfig(partial_complement_dir=partial_dir)

    partial = load_partial_context(config)

    assert partial.partial_sample_id == "P1"
    assert partial.partial_readiness_flag == "PARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION"
