from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    run_h4_transition_scenario_sensitive_review,
)
from sqre.h4_transition_scenario_sensitive_review.reports import build_report_text


FORBIDDEN = [
    "buy",
    "sell",
    "entry",
    "exit",
    "trade signal",
    "trade setup",
    "take profit",
    "stop loss",
    "profitable",
    "opportunity",
    "edge",
    "best timeframe",
    "ranking",
    "should trade",
    "predicts",
    "optimal",
]


def test_report_contains_required_sections_and_excludes_forbidden_language(tmp_path: Path):
    dispersion_dir, deep_dive_dir = write_transition_sensitive_inputs(tmp_path)
    result = run_h4_transition_scenario_sensitive_review(
        dispersion_dir,
        deep_dive_dir,
        tmp_path / "out",
        tmp_path / "out" / "report.txt",
    )

    text = build_report_text(result)

    for section in [
        "SQRE H4 Transition Scenario-Sensitive Profile Review",
        "Generated At",
        "Input Directories",
        "Transition Scenario-Sensitive Profile Overview",
        "Focus Transition Review",
        "Transition Family Sensitivity Review",
        "Source State Sensitivity Review",
        "Target State Sensitivity Review",
        "Forward Window Sensitivity Review",
        "Scenario Recurrent Deviation Review",
        "Deviation Driver Review",
        "Near Aggregation Candidate Review",
        "Research Readiness Assessment",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
    ]:
        assert section in text
    lowered = text.lower()
    assert all(term not in lowered for term in FORBIDDEN)
