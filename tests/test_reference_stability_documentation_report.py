from __future__ import annotations

from sqre.reference_stability_documentation.reports import build_report_text
from sqre.reference_stability_documentation.scope_safety_review import build_scope_safety_review, scope_safety_class
from tests.test_reference_stability_documentation_loader import write_synthetic_documentation_inputs
from sqre.reference_stability_documentation.reference_stability_documentation_pipeline import (
    ReferenceStabilityDocumentationPipeline,
)


def test_report_includes_all_required_sections(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)
    result = ReferenceStabilityDocumentationPipeline(config).run()
    report = build_report_text(result)

    for section in [
        "Generated At",
        "Input Directories",
        "Output Directory",
        "Source Inventory",
        "Stability Interpretation Guide",
        "Evidence Usage Policy",
        "Dashboard Reading Guide",
        "Limitations Documentation",
        "Follow-Up Plan",
        "Scope Safety Review",
        "Readiness Assessment",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
        "Scope Statements",
        "Markdown Output",
    ]:
        assert section in report


def test_report_excludes_forbidden_language_except_negative_scope_statements(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)
    result = ReferenceStabilityDocumentationPipeline(config).run()
    review = build_scope_safety_review(True, {"report": config.report_path.read_text(encoding="utf-8")})

    assert scope_safety_class(review) == "DOCUMENTATION_SCOPE_SAFE"
