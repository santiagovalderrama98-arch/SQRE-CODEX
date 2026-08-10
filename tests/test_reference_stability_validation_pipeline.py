from __future__ import annotations

from pathlib import Path

from sqre.reference_stability_validation.reference_stability_validation_pipeline import ReferenceStabilityValidationPipeline
from tests.test_reference_stability_validation_loader import write_synthetic_inputs


def test_pipeline_writes_all_expected_outputs(tmp_path):
    config = write_synthetic_inputs(tmp_path)

    ReferenceStabilityValidationPipeline(config).run()

    expected = [
        "reference_stability_source_inventory.csv",
        "reference_population_review.csv",
        "reference_horizon_stability_review.csv",
        "reference_granularity_stability_review.csv",
        "reference_sample_adequacy_review.csv",
        "reference_dispersion_stability_review.csv",
        "reference_directional_consistency_review.csv",
        "reference_match_level_stability_review.csv",
        "dashboard_reference_stability_review.csv",
        "reference_stability_scorecard.csv",
        "reference_stability_validation_summary.csv",
        "reference_stability_validation_report.txt",
    ]
    for filename in expected:
        assert Path(config.output_dir / filename).exists()
