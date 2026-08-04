from __future__ import annotations

import pandas as pd

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.h4_d1_aligned_forward_outcome_pipeline import (
    H4D1AlignedForwardOutcomeResearchPipeline,
)
from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_pipeline_writes_all_expected_outputs(tmp_path):
    alignment_dir, synchronized_dir, contextual_dir = write_forward_outcome_inputs(tmp_path)
    output_dir = tmp_path / "out"
    result = H4D1AlignedForwardOutcomeResearchPipeline(
        H4D1AlignedForwardOutcomeResearchConfig(
            same_time_alignment_dir=alignment_dir,
            synchronized_data_dir=synchronized_dir,
            contextual_transition_dir=contextual_dir,
            output_dir=output_dir,
            report_path=output_dir / "report.txt",
            forward_horizons=(1, 3),
            minimum_outcome_sample_size=1,
            minimum_context_outcome_sample_size=1,
        )
    ).run()

    assert result.summary is not None
    assert (output_dir / "h4_d1_aligned_forward_outcome_source_inventory.csv").exists()
    assert (output_dir / "h4_transition_forward_outcomes.csv").exists()
    assert (output_dir / "h4_d1_forward_outcome_profiles.csv").exists()
    assert (output_dir / "h4_d1_forward_outcome_dispersion_review.csv").exists()
    assert (output_dir / "h4_d1_forward_outcome_sample_adequacy_review.csv").exists()
    assert (output_dir / "h4_d1_aligned_forward_outcome_research_summary.csv").exists()
    assert result.report_path.exists()
    summary = pd.read_csv(output_dir / "h4_d1_aligned_forward_outcome_research_summary.csv")
    assert summary.loc[0, "Forward_Outcome_Row_Count"] == 4
    assert summary.loc[0, "Outcome_Profile_Count"] > 0
