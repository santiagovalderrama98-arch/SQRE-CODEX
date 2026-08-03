from pathlib import Path

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.scenario_inventory_loader import load_base_scenario_inventory


def test_scenario_inventory_loads_scenario_and_period_bounds(tmp_path: Path):
    validation = tmp_path / "validation"
    validation.mkdir()
    (validation / "h4_d1_validation_summary.csv").write_text(
        "Scenario_ID,Symbol,Timeframe,Period_Start,Period_End,OHLC_File,Transitions_Generated\n"
        "SCN_1,EURUSD,H4,2026-01-01,2026-01-31,raw.csv,2\n",
        encoding="utf-8",
    )
    config = H4TimestampedContextTableGenerationConfig(
        h4_d1_validation_dir=validation,
        h4_combined_context_dir=tmp_path / "combined",
        h4_d1_structural_research_dir=tmp_path / "research",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out/report.txt",
    )

    rows = load_base_scenario_inventory(config)

    assert rows[0].scenario_id == "SCN_1"
    assert rows[0].period_start == "2026-01-01"
    assert rows[0].period_end == "2026-01-31"
    assert rows[0].transitions_generated == 2
