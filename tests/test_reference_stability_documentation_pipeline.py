from __future__ import annotations

from pathlib import Path

from sqre.reference_stability_documentation.reference_stability_documentation_pipeline import (
    ReferenceStabilityDocumentationPipeline,
)
from tests.test_reference_stability_documentation_loader import write_synthetic_documentation_inputs


def test_pipeline_writes_all_expected_csv_txt_and_markdown_outputs(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)

    ReferenceStabilityDocumentationPipeline(config).run()

    expected = [
        "reference_stability_documentation_source_inventory.csv",
        "reference_stability_interpretation_guide.csv",
        "reference_evidence_usage_policy.csv",
        "reference_dashboard_reading_guide.csv",
        "reference_stability_limitations_documentation.csv",
        "reference_stability_follow_up_plan.csv",
        "reference_stability_documentation_scope_safety_review.csv",
        "reference_stability_documentation_summary.csv",
        "reference_stability_documentation_report.txt",
        "reference_stability_documentation.md",
    ]
    for filename in expected:
        assert Path(config.output_dir / filename).exists()
