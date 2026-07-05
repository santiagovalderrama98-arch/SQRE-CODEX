from __future__ import annotations

import pandas as pd

from sqre.market_structure.market_structure_pipeline import MarketStructurePipeline


def test_market_structure_pipeline_writes_all_outputs(tmp_path) -> None:
    events_path = tmp_path / "events.csv"
    output_dir = tmp_path / "processed"
    report_path = tmp_path / "reports" / "market_structure_report.txt"

    pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=8, freq="5min"),
            "EventType": [
                "PIVOT_LOW",
                "RANGE_EXPANSION",
                "PIVOT_HIGH",
                "SMALL_CANDLE",
                "PIVOT_LOW",
                "LARGE_CANDLE",
                "SWING_HIGH",
                "PIVOT_LOW",
            ],
            "Symbol": ["EURUSD"] * 8,
            "Timeframe": ["M5"] * 8,
            "Price": [1.1000, 1.1005, 1.1010, 1.1008, 1.1002, 1.1012, 1.1020, 1.1010],
            "Value": [1.1000, 5, 1.1010, 1, 1.1002, 1, 1.1020, 1.1010],
        }
    ).to_csv(events_path, index=False)

    result = MarketStructurePipeline().run(events_path=events_path, output_dir=output_dir, report_path=report_path)

    assert result.success
    assert result.events_processed == 8
    assert result.structures_detected == 1
    assert result.structures_path.exists()
    assert result.structure_events_path.exists()
    assert result.structural_units_path.exists()
    assert result.structural_fingerprints_path.exists()
    assert result.report_path.exists()

    structures = pd.read_csv(result.structures_path)
    fingerprints = pd.read_csv(result.structural_fingerprints_path)
    links = pd.read_csv(result.structure_events_path)
    units = pd.read_csv(result.structural_units_path)

    assert {"Structure_ID", "Persistence_Index", "Structural_Confidence"}.issubset(structures.columns)
    assert {"Structure_ID", "Persistence", "Confidence"}.issubset(fingerprints.columns)
    assert {"Structure_ID", "Event_ID", "Role_In_Structure"}.issubset(links.columns)
    assert {"Unit_ID", "Unit_Type", "Confidence"}.issubset(units.columns)
    assert "SQRE Market Structure Report" in report_path.read_text(encoding="utf-8")
