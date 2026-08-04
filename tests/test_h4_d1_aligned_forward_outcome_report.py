from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.h4_d1_aligned_forward_outcome_pipeline import (
    H4D1AlignedForwardOutcomeResearchPipeline,
)
from sqre.h4_d1_aligned_forward_outcome_research.reports import FORBIDDEN_REPORT_TERMS, build_report_text
from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_report_includes_required_sections_and_scope(tmp_path):
    alignment_dir, synchronized_dir, contextual_dir = write_forward_outcome_inputs(tmp_path)
    output_dir = tmp_path / "out"
    result = H4D1AlignedForwardOutcomeResearchPipeline(
        H4D1AlignedForwardOutcomeResearchConfig(
            same_time_alignment_dir=alignment_dir,
            synchronized_data_dir=synchronized_dir,
            contextual_transition_dir=contextual_dir,
            output_dir=output_dir,
            report_path=output_dir / "report.txt",
            forward_horizons=(1,),
        )
    ).run()

    text = build_report_text(result)

    assert "Forward Outcome Calculation" in text
    assert "Context Granularity Outcome Profiles" in text
    assert "This phase does not generate trading signals." in text
    assert "This phase does not decide whether any context is favorable or unfavorable." in text
    assert all(term not in text.lower() for term in FORBIDDEN_REPORT_TERMS)
