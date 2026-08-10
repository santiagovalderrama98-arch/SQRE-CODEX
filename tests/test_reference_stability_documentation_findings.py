from __future__ import annotations

from sqre.reference_stability_documentation.findings import build_summary
from sqre.reference_stability_documentation.reference_stability_documentation_pipeline import (
    ReferenceStabilityDocumentationPipeline,
)
from tests.test_reference_stability_documentation_loader import write_synthetic_documentation_inputs


def test_findings_produce_correct_readiness_flag(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)
    result = ReferenceStabilityDocumentationPipeline(config).run()

    assert result.summary is not None
    assert result.summary.reference_stability_documentation_readiness_flag in {
        "READY_FOR_DASHBOARD_STABILITY_INDICATORS",
        "PARTIAL_READY_FOR_DASHBOARD_STABILITY_INDICATORS",
    }


def test_findings_report_input_missing_when_required_inputs_missing(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)
    result = ReferenceStabilityDocumentationPipeline(config).run()
    summary = build_summary(
        config,
        [],
        result.interpretation_guide,
        result.evidence_usage_policy,
        result.dashboard_reading_guide,
        result.limitations_documentation,
        result.follow_up_plan,
        result.scope_safety_review,
    )

    assert summary.reference_stability_documentation_readiness_flag != "INPUT_COMPLETENESS_REVIEW_REQUIRED"
