from __future__ import annotations

from sqre.dashboard_stability_indicators.scope_safety_review import build_scope_safety_review, scope_safety_class


def test_scope_safety_review_detects_forbidden_operational_language():
    review = build_scope_safety_review(True, {"unsafe": "This text says buy now."})

    assert scope_safety_class(review) == "DASHBOARD_STABILITY_SCOPE_VIOLATION"


def test_scope_safety_review_allows_explicit_negative_scope_statements():
    review = build_scope_safety_review(True, {"safe": "This phase does not generate buy or sell guidance."})

    assert scope_safety_class(review) == "DASHBOARD_STABILITY_SCOPE_SAFE"
