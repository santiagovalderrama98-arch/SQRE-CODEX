from sqre.manual_research_dashboard_review.scope_safety_review import (
    build_scope_safety_review,
    count_unsafe_occurrences,
)


def test_scope_safety_detects_forbidden_operational_language():
    review = build_scope_safety_review({"prototype_report": "This says buy now.", "prototype_html": "<p>ok</p>"})

    buy_row = review[(review["Reviewed_Source"] == "Prototype Report") & (review["Forbidden_Term"] == "buy")].iloc[0]
    assert buy_row["Scope_Safety_Class"] == "SCOPE_VIOLATION"


def test_scope_safety_ignores_explicit_negative_scope_statement():
    assert count_unsafe_occurrences("This phase does not generate a trade signal.", "trade signal") == 0
