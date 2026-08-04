from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.d1_regime_context_adequacy_pipeline import (
    D1RegimeContextAdequacyPipeline,
)
from tests.d1_regime_context_adequacy_test_utils import (
    write_contextual_transition_inputs,
    write_optional_supporting_inputs,
)


def test_pipeline_writes_expected_outputs(tmp_path):
    contextual_dir = tmp_path / "contextual"
    alignment_dir = tmp_path / "alignment"
    timestamped_dir = tmp_path / "timestamped"
    output_dir = tmp_path / "out"
    write_contextual_transition_inputs(contextual_dir)
    write_optional_supporting_inputs(alignment_dir, timestamped_dir)

    result = D1RegimeContextAdequacyPipeline(
        D1RegimeContextAdequacyReviewConfig(
            contextual_transition_dir=contextual_dir,
            same_time_alignment_dir=alignment_dir,
            timestamped_state_regime_dir=timestamped_dir,
            output_dir=output_dir,
            report_path=output_dir / "report.txt",
        )
    ).run()

    assert result.summary is not None
    assert (output_dir / "d1_regime_context_adequacy_source_inventory.csv").exists()
    assert (output_dir / "d1_context_inventory.csv").exists()
    assert (output_dir / "h4_transition_d1_fragmentation_review.csv").exists()
    assert (output_dir / "h4_transition_sample_loss_review.csv").exists()
    assert (output_dir / "d1_context_sample_adequacy_review.csv").exists()
    assert (output_dir / "d1_context_aggregation_candidate_review.csv").exists()
    assert (output_dir / "d1_regime_context_adequacy_review_summary.csv").exists()
    assert result.report_path.exists()
    summary = pd.read_csv(output_dir / "d1_regime_context_adequacy_review_summary.csv")
    assert summary.loc[0, "Context_Profile_Count"] == 5
    assert summary.loc[0, "Low_Or_Insufficient_Context_Count"] == 3
