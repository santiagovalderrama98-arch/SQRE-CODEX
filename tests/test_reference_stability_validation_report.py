from __future__ import annotations

from sqre.reference_stability_validation.reference_stability_validation_pipeline import ReferenceStabilityValidationPipeline
from tests.test_reference_stability_validation_loader import write_synthetic_inputs


def test_report_includes_required_sections(tmp_path):
    config = write_synthetic_inputs(tmp_path)

    result = ReferenceStabilityValidationPipeline(config).run()
    text = result.report_path.read_text()

    assert "SQRE Reference Stability Validation" in text
    assert "Reference Stability Scorecard" in text
    assert "Do Not Change Yet" in text
    assert "Scope Statements" in text


def test_report_excludes_operational_language_except_negative_scope_statements(tmp_path):
    config = write_synthetic_inputs(tmp_path)

    text = ReferenceStabilityValidationPipeline(config).run().report_path.read_text().lower()

    assert "does not generate trading signals" in text
    assert "does not generate operational recommendations" in text
    for forbidden in ["buy", "sell", "take profit", "stop loss", "should trade"]:
        assert forbidden not in text
