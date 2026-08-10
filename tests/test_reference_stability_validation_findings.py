from __future__ import annotations

from sqre.reference_stability_validation.reference_stability_validation_pipeline import ReferenceStabilityValidationPipeline
from tests.test_reference_stability_validation_loader import write_synthetic_inputs


def test_findings_produce_correct_readiness_flag(tmp_path):
    config = write_synthetic_inputs(tmp_path)

    result = ReferenceStabilityValidationPipeline(config).run()

    assert result.summary is not None
    assert result.summary.reference_stability_readiness_flag in {
        "READY_FOR_REFERENCE_STABILITY_DOCUMENTATION",
        "PARTIAL_READY_FOR_REFERENCE_STABILITY_DOCUMENTATION",
    }
