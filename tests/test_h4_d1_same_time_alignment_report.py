from pathlib import Path

from sqre.h4_d1_same_time_alignment_table.config import H4D1SameTimeAlignmentConfig
from sqre.h4_d1_same_time_alignment_table.h4_d1_same_time_alignment_pipeline import (
    run_h4_d1_same_time_alignment_table,
)
from sqre.h4_d1_same_time_alignment_table.reports import build_report_text
from tests.h4_d1_same_time_alignment_test_utils import write_same_time_alignment_fixture


def test_report_includes_required_sections_and_scope_language(tmp_path: Path):
    timestamped_dir, synchronized_dir = write_same_time_alignment_fixture(tmp_path)
    result = run_h4_d1_same_time_alignment_table(
        H4D1SameTimeAlignmentConfig(
            timestamped_state_regime_dir=timestamped_dir,
            synchronized_data_dir=synchronized_dir,
            output_dir=tmp_path / "out",
            report_path=tmp_path / "out" / "report.txt",
        )
    )

    text = build_report_text(result)

    for section in [
        "Generated At",
        "Input Directories",
        "Output Directory",
        "Source Inventory",
        "H4 Transition to D1 Same-Time Alignment",
        "H4 State to D1 Same-Time Alignment",
        "Alignment Coverage Review",
        "Unmatched Alignment Review",
        "Readiness Assessment",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
    ]:
        assert section in text
    assert "This phase builds same-time alignment tables only." in text
    assert "This phase does not interpret the meaning of aligned H4/D1 contexts." in text
    assert "This phase does not generate trading signals." in text


def test_report_excludes_forbidden_operational_language(tmp_path: Path):
    timestamped_dir, synchronized_dir = write_same_time_alignment_fixture(tmp_path)
    result = run_h4_d1_same_time_alignment_table(
        H4D1SameTimeAlignmentConfig(
            timestamped_state_regime_dir=timestamped_dir,
            synchronized_data_dir=synchronized_dir,
            output_dir=tmp_path / "out",
            report_path=tmp_path / "out" / "report.txt",
        )
    )
    text = result.report_path.read_text(encoding="utf-8").lower()

    for forbidden in [
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
        "predicts",
        "optimal",
        "should trade",
    ]:
        assert forbidden not in text
