from pathlib import Path

from sqre.d1_regime_normalized_research.models import D1RegimeResearchResult
from sqre.d1_regime_normalized_research.reports import write_d1_regime_research_report


def test_report_includes_required_sections_and_excludes_forbidden_language(tmp_path):
    report = tmp_path / "report.txt"
    result = D1RegimeResearchResult(
        config_path="config.yaml",
        input_validation_summary="summary.csv",
        validation_output_dir="validation",
        output_dir=tmp_path,
        report_path=report,
    )

    write_d1_regime_research_report(report, result)
    text = report.read_text(encoding="utf-8")

    assert "SQRE D1 Regime-Normalized Price Outcome Research Report" in text
    assert "Scenario / Regime Inventory" in text
    assert "Regime Sensitivity Review" in text
    assert "No comparative ordering is produced." in text
    assert not _contains_forbidden_language(text)


def _contains_forbidden_language(text: str) -> bool:
    forbidden = [
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
    lower = text.lower()
    return any(term in lower for term in forbidden)
