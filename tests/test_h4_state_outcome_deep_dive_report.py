from pathlib import Path

from h4_state_deep_dive_test_utils import write_h4_deep_dive_inputs
from sqre.h4_state_outcome_deep_dive.h4_state_outcome_deep_dive_pipeline import run_h4_state_outcome_deep_dive


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


def test_report_contains_required_sections_without_forbidden_language(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    output_dir = tmp_path / "output"
    report_path = output_dir / "report.txt"
    write_h4_deep_dive_inputs(research_dir, validation_dir)

    run_h4_state_outcome_deep_dive(research_dir, validation_dir, output_dir, report_path)
    report = report_path.read_text(encoding="utf-8")

    for section in [
        "SQRE H4 Research-Ready State Outcome Deep Dive",
        "Executive Diagnostic Summary",
        "Selected H4 State Profiles",
        "DIRECTIONAL_DISPLACEMENT Deep Dive",
        "DIRECTIONAL_EXPANSION Deep Dive",
        "VOLATILE_ROTATION Review",
        "Sample-Constrained State Review",
        "Scenario Breakdown Review",
        "Outcome Dispersion Review",
        "Research Readiness Assessment",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
    ]:
        assert section in report
    lower_report = report.lower()
    assert not any(term in lower_report for term in FORBIDDEN_REPORT_TERMS)
