from pathlib import Path

import pandas as pd

from sqre.h4_d1_same_time_alignment_table.config import H4D1SameTimeAlignmentConfig
from sqre.h4_d1_same_time_alignment_table.h4_d1_same_time_alignment_pipeline import (
    run_h4_d1_same_time_alignment_table,
)
from tests.h4_d1_same_time_alignment_test_utils import write_same_time_alignment_fixture


def test_pipeline_writes_all_expected_outputs(tmp_path: Path):
    timestamped_dir, synchronized_dir = write_same_time_alignment_fixture(tmp_path)
    output_dir = tmp_path / "out"

    result = run_h4_d1_same_time_alignment_table(
        H4D1SameTimeAlignmentConfig(
            timestamped_state_regime_dir=timestamped_dir,
            synchronized_data_dir=synchronized_dir,
            output_dir=output_dir,
            report_path=output_dir / "h4_d1_same_time_alignment_report.txt",
        )
    )

    for filename in [
        "h4_d1_same_time_source_inventory.csv",
        "h4_transition_d1_same_time_alignment.csv",
        "h4_state_d1_same_time_alignment.csv",
        "h4_d1_same_time_alignment_coverage_review.csv",
        "h4_d1_unmatched_alignment_review.csv",
        "h4_d1_same_time_alignment_summary.csv",
        "h4_d1_same_time_alignment_report.txt",
    ]:
        assert (output_dir / filename).exists()
    assert result.summary is not None
    assert result.summary.h4_d1_same_time_alignment_readiness_flag == "READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW"


def test_pipeline_handles_missing_inputs_without_failure(tmp_path: Path):
    output_dir = tmp_path / "out"

    run_h4_d1_same_time_alignment_table(
        H4D1SameTimeAlignmentConfig(
            timestamped_state_regime_dir=tmp_path / "missing_timestamped",
            synchronized_data_dir=tmp_path / "missing_sync",
            output_dir=output_dir,
            report_path=output_dir / "report.txt",
        )
    )

    summary = pd.read_csv(output_dir / "h4_d1_same_time_alignment_summary.csv")
    assert summary["H4_D1_Same_Time_Alignment_Readiness_Flag"].iloc[0] == "INPUT_COMPLETENESS_REVIEW_REQUIRED"
