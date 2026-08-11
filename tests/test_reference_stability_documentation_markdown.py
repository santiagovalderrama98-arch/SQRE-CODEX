from __future__ import annotations

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig
from sqre.reference_stability_documentation.markdown_renderer import render_markdown
from sqre.reference_stability_documentation.reference_stability_documentation_pipeline import (
    ReferenceStabilityDocumentationPipeline,
)
from sqre.reference_stability_documentation.scope_safety_review import build_scope_safety_review, scope_safety_class
from tests.test_reference_stability_documentation_loader import write_synthetic_documentation_inputs


def test_markdown_renderer_writes_all_required_sections(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)
    result = ReferenceStabilityDocumentationPipeline(config).run()

    text = render_markdown(
        ReferenceStabilityDocumentationConfig(),
        result.interpretation_guide,
        result.evidence_usage_policy,
        result.dashboard_reading_guide,
        result.limitations_documentation,
        result.follow_up_plan,
        result.summary,
    )

    for section in [
        "# SQRE Reference Stability Documentation",
        "## Purpose",
        "## Current Evidence Base",
        "## Stability Summary",
        "## How to Read Stable Evidence",
        "## How to Read Partial Evidence",
        "## How to Read Directionally Unstable Evidence",
        "## How to Read Fallback-Dependent Evidence",
        "## Dashboard Reading Guide",
        "## What the Dashboard Must Not Be Used For",
        "## Limitations",
        "## Recommended Follow-Up",
        "## Scope Statements",
    ]:
        assert section in text


def test_markdown_excludes_forbidden_language_except_negative_scope_statements(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)
    result = ReferenceStabilityDocumentationPipeline(config).run()

    text = config.markdown_path.read_text(encoding="utf-8")
    review = build_scope_safety_review(True, {"markdown": text})

    assert scope_safety_class(review) == "DOCUMENTATION_SCOPE_SAFE"
