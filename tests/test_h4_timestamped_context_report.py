from pathlib import Path

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.h4_timestamped_context_table_pipeline import (
    run_h4_timestamped_context_table_generation,
)


def test_report_includes_required_sections_and_excludes_operational_language(tmp_path: Path):
    validation = tmp_path / "validation"
    validation.mkdir()
    (validation / "h4_d1_validation_summary.csv").write_text(
        "Scenario_ID,Symbol,Timeframe,Period_Start,Period_End,Transitions_Generated\n"
        "SCN_1,EURUSD,H4,2026-01-01,2026-01-31,1\n",
        encoding="utf-8",
    )
    config = H4TimestampedContextTableGenerationConfig(
        h4_combined_context_dir=tmp_path / "combined",
        h4_d1_validation_dir=validation,
        h4_d1_structural_research_dir=tmp_path / "research",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out/report.txt",
    )

    result = run_h4_timestamped_context_table_generation(config)
    report = result.report_path.read_text(encoding="utf-8")

    assert "Source Inventory" in report
    assert "Scenario Inventory" in report
    assert "This phase does not align H4 to D1 yet." in report
    assert "This phase does not perform same-time H4/D1 interpretation." in report
    forbidden_terms = ["buy", "sell", "trade signal", "take profit", "stop loss", "should trade"]
    assert not any(term in report.lower() for term in forbidden_terms)
