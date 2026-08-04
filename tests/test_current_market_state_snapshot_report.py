import pandas as pd
import pytest

from sqre.current_market_state_snapshot_research.models import CurrentMarketStateSnapshotResearchResult
from sqre.current_market_state_snapshot_research.reports import build_report_text, write_outputs


def test_report_contains_required_scope_statements(tmp_path):
    result = CurrentMarketStateSnapshotResearchResult(
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        snapshot_context=pd.DataFrame([{"Snapshot_Mode": "USER_SUPPLIED_SNAPSHOT"}]),
    )

    text = build_report_text(result)

    assert "research-only current or latest-available structural snapshot workflow" in text
    assert "does not generate trading signals" in text
    assert "does not create a Decision Engine" in text


def test_report_writes_summary_files(tmp_path):
    result = CurrentMarketStateSnapshotResearchResult(output_dir=tmp_path, report_path=tmp_path / "report.txt")

    write_outputs(result)

    assert (tmp_path / "current_market_state_snapshot_research_summary.csv").exists()
    assert (tmp_path / "report.txt").exists()


def test_report_rejects_forbidden_operational_language(tmp_path):
    result = CurrentMarketStateSnapshotResearchResult(
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        snapshot_diagnostic_review=pd.DataFrame(
            [{"Diagnostic_Category": "X", "Diagnostic_Status": "Y", "Diagnostic_Message": "buy"}]
        ),
    )

    with pytest.raises(ValueError):
        write_outputs(result)
