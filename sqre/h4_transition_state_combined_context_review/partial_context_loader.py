"""Load partial complementary context inputs."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.loader import first_row, read_optional_csv, text_value
from sqre.h4_transition_state_combined_context_review.models import PartialContext


def load_partial_context(config: H4TransitionStateCombinedContextReviewConfig) -> PartialContext:
    interpretation = first_row(
        read_optional_csv(config.partial_complement_dir / "h4_partial_baseline_interpretation_matrix.csv")
    )
    caveat = first_row(read_optional_csv(config.partial_complement_dir / "h4_partial_sample_caveat_review.csv"))
    summary = first_row(
        read_optional_csv(config.partial_complement_dir / "h4_partial_complementary_dispersion_summary.csv")
    )
    if interpretation is None and caveat is None and summary is None:
        return PartialContext(partial_sample_label=config.partial_sample_label)
    return PartialContext(
        partial_sample_id=text_value(interpretation, ["Candidate_ID"], "eurusd_h4_period_5_partial") if interpretation is not None else "eurusd_h4_period_5_partial",
        partial_sample_label=text_value(interpretation, ["Sample_Label"], config.partial_sample_label) if interpretation is not None else config.partial_sample_label,
        partial_interpretation_class=text_value(
            interpretation,
            ["Partial_Baseline_Interpretation_Class", "Dominant_Partial_Baseline_Interpretation"],
            text_value(summary, ["Dominant_Partial_Baseline_Interpretation"], "PARTIAL_CONTEXT_UNAVAILABLE") if summary is not None else "PARTIAL_CONTEXT_UNAVAILABLE",
        ) if interpretation is not None else text_value(summary, ["Dominant_Partial_Baseline_Interpretation"], "PARTIAL_CONTEXT_UNAVAILABLE"),
        partial_readiness_flag=text_value(
            summary,
            ["H4_Partial_Complementary_Readiness_Flag"],
            "PARTIAL_CONTEXT_UNAVAILABLE",
        ) if summary is not None else "PARTIAL_CONTEXT_UNAVAILABLE",
        partial_caveat_class=text_value(
            caveat,
            ["Partial_Sample_Caveat_Class"],
            "PARTIAL_CONTEXT_UNAVAILABLE",
        ) if caveat is not None else "PARTIAL_CONTEXT_UNAVAILABLE",
    )
