from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.models import H4TimestampedStateTransitionResult
from sqre.h4_timestamped_state_transition_outputs.reports import FORBIDDEN_REPORT_TERMS, build_report_text


def test_report_includes_all_required_sections(tmp_path: Path):
    text = build_report_text(H4TimestampedStateTransitionResult(output_dir=tmp_path, report_path=tmp_path / "report.txt"))

    for section in [
        "Generated At",
        "Input Directories",
        "Output Directory",
        "Source Inventory",
        "Scenario Inventory",
        "Timestamped Market States",
        "Timestamped State Transitions",
        "Coverage Review",
        "Missing Output Review",
        "Generation Summary",
        "Research Readiness Assessment",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
    ]:
        assert section in text


def test_report_explicitly_states_d1_alignment_is_not_performed(tmp_path: Path):
    text = build_report_text(H4TimestampedStateTransitionResult(output_dir=tmp_path, report_path=tmp_path / "report.txt"))

    assert "This phase does not align H4 to D1." in text
    assert "This phase does not perform same-time H4/D1 interpretation." in text


def test_report_excludes_forbidden_operational_language(tmp_path: Path):
    text = build_report_text(H4TimestampedStateTransitionResult(output_dir=tmp_path, report_path=tmp_path / "report.txt"))
    lowered = text.lower()

    assert all(term not in lowered for term in FORBIDDEN_REPORT_TERMS)
