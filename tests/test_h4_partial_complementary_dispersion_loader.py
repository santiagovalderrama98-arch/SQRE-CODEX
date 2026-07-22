from pathlib import Path

import pandas as pd

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.partial_sample_loader import (
    load_partial_sample_review,
)


def test_loader_reads_synthetic_partial_validation_summary(tmp_path: Path):
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    pd.DataFrame(
        [
            {
                "Candidate_ID": "eurusd_h4_period_5_partial",
                "Sample_Label": "PARTIAL_SAMPLE",
                "Coverage_Ratio": 0.5,
            }
        ]
    ).to_csv(partial_dir / "h4_partial_candidate_inventory.csv", index=False)
    pd.DataFrame(
        [
            {
                "Candidate_ID": "eurusd_h4_period_5_partial",
                "Sample_Label": "PARTIAL_SAMPLE",
                "Run_Status": "COMPLETED",
                "Condition_Profile_Count": 48,
            }
        ]
    ).to_csv(partial_dir / "h4_partial_validation_run_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "Candidate_ID": "eurusd_h4_period_5_partial",
                "Sample_Label": "PARTIAL_SAMPLE",
                "Sample_Adequacy_Class": "PARTIAL_SAMPLE_RESEARCH_USABLE",
            }
        ]
    ).to_csv(partial_dir / "h4_partial_sample_adequacy_review.csv", index=False)
    pd.DataFrame(
        [
            {
                "Candidate_ID": "eurusd_h4_period_5_partial",
                "Sample_Label": "PARTIAL_SAMPLE",
                "Partial_Comparison_Class": "CONSISTENT_WITH_BASELINE_RANGE",
            }
        ]
    ).to_csv(partial_dir / "h4_partial_vs_baseline_comparison.csv", index=False)

    rows = load_partial_sample_review(H4PartialComplementaryDispersionReviewConfig(partial_validation_dir=partial_dir))

    assert len(rows) == 1
    assert rows[0].candidate_id == "eurusd_h4_period_5_partial"
    assert rows[0].coverage_ratio == 0.5
    assert rows[0].partial_sample_status == "PARTIAL_VALIDATED"


def test_loader_reads_synthetic_partial_comparison(tmp_path: Path):
    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    pd.DataFrame(
        [
            {
                "Candidate_ID": "eurusd_h4_period_5_partial",
                "Sample_Label": "PARTIAL_SAMPLE",
                "Run_Status": "COMPLETED",
                "Condition_Profile_Count": 24,
            }
        ]
    ).to_csv(partial_dir / "h4_partial_validation_run_summary.csv", index=False)
    pd.DataFrame(
        [{"Candidate_ID": "eurusd_h4_period_5_partial", "Sample_Adequacy_Class": "PARTIAL_SAMPLE_LIMITED"}]
    ).to_csv(partial_dir / "h4_partial_sample_adequacy_review.csv", index=False)
    pd.DataFrame(
        [{"Candidate_ID": "eurusd_h4_period_5_partial", "Partial_Comparison_Class": "ELEVATED_VS_BASELINE"}]
    ).to_csv(partial_dir / "h4_partial_vs_baseline_comparison.csv", index=False)

    rows = load_partial_sample_review(H4PartialComplementaryDispersionReviewConfig(partial_validation_dir=partial_dir))

    assert rows[0].partial_comparison_class == "ELEVATED_VS_BASELINE"
    assert rows[0].partial_sample_status == "PARTIAL_LIMITED"
