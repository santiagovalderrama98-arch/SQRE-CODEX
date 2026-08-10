from __future__ import annotations

from sqre.reference_stability_documentation.scope_safety_review import build_scope_safety_review, scope_safety_class


def test_scope_safety_review_detects_forbidden_operational_language():
    review = build_scope_safety_review(True, {"doc": "This dashboard says buy now."})

    assert scope_safety_class(review) == "DOCUMENTATION_SCOPE_VIOLATION"


def test_scope_safety_review_allows_explicit_negative_scope_statements():
    review = build_scope_safety_review(True, {"doc": "This phase does not generate trade signal output."})

    assert scope_safety_class(review) == "DOCUMENTATION_SCOPE_SAFE"
