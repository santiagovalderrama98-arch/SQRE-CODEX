from pathlib import Path

from test_h4_transition_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_transition_scenario_dispersion_review.h4_transition_scenario_dispersion_review_pipeline import run_h4_transition_scenario_dispersion_review


FORBIDDEN_REPORT_TERMS = [
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


def test_report_includes_required_sections_and_excludes_forbidden_language(tmp_path: Path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    report_path = output_dir / "report.txt"
    write_review_inputs(input_dir)

    run_h4_transition_scenario_dispersion_review(input_dir, output_dir, report_path)
    report = report_path.read_text(encoding="utf-8")

    for section in [
        "SQRE H4 Transition Scenario Dispersion Review",
        "Executive Diagnostic Summary",
        "Transition Profile Dispersion Overview",
        "Transition Family Dispersion Review",
        "Source State Dispersion Review",
        "Target State Dispersion Review",
        "Forward Window Dispersion Review",
        "Scenario Contribution Review",
        "Aggregation Candidate Review",
        "Scenario-Sensitive Transition Review",
        "Sample-Constrained Transition Review",
        "Research Readiness Assessment",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
    ]:
        assert section in report
    lower_report = report.lower()
    assert not any(term in lower_report for term in FORBIDDEN_REPORT_TERMS)
