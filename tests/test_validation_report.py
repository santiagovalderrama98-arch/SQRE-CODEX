from pathlib import Path

from sqre.validation.models import COMPLETED, ScenarioMetrics, ValidationConfig, ValidationScenario, ValidationSummary
from sqre.validation.reports import write_validation_report


def test_validation_report_contains_descriptive_sections(tmp_path):
    scenario = ValidationScenario(
        scenario_id="eurusd_m5",
        symbol="EURUSD",
        timeframe="M5",
        ohlc_path=Path("data/raw/EURUSD_M5.csv"),
        max_structure_duration_seconds=14400,
        forward_candles=[3, 6, 12],
        pip_size=0.0001,
        minimum_sample_size=5,
        output_root=tmp_path,
    )
    config = ValidationConfig(
        validation_name="sample_validation",
        symbol="EURUSD",
        pip_size=0.0001,
        minimum_sample_size=5,
        scenarios=[scenario],
    )
    summary = ValidationSummary(
        validation_name="sample_validation",
        scenarios_configured=1,
        scenarios_selected=1,
        scenarios_completed=1,
        scenarios_missing_input=0,
        scenarios_failed=0,
        scenarios_skipped=0,
        summary_csv_path=tmp_path / "summary.csv",
        report_path=tmp_path / "report.txt",
    )
    metrics = ScenarioMetrics(
        scenario_id="eurusd_m5",
        status=COMPLETED,
        message="Scenario completed",
        symbol="EURUSD",
        timeframe="M5",
        ohlc_file="data/raw/EURUSD_M5.csv",
        ohlc_rows=100,
        structures_detected=10,
        states_generated=10,
        transitions_generated=9,
        price_outcomes_generated=20,
    )

    path = write_validation_report(tmp_path / "report.txt", config=config, summary=summary, metrics=[metrics])
    text = path.read_text(encoding="utf-8")

    assert "SQRE Multi-Scenario & Multi-Timeframe Validation Report" in text
    assert "Scenario Overview" in text
    assert "Price Outcome Research Comparison" in text
    assert "No execution guidance is produced." in text
