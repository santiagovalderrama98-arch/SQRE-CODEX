from pathlib import Path

import pandas as pd
import pytest

from sqre.calibration_review.loader import load_validation_summaries, load_validation_summary_csv


def test_load_validation_summary_csv_supports_case_insensitive_columns(tmp_path: Path):
    csv_path = tmp_path / "summary.csv"
    pd.DataFrame(
        [
            {
                "scenario_id": "eurusd_m5_period_1",
                "status": "COMPLETED",
                "symbol": "EURUSD",
                "timeframe": "M5",
                "conditions_evaluated": 55,
                "low_sample_conditions_research": 47,
            }
        ]
    ).to_csv(csv_path, index=False)

    rows = load_validation_summary_csv(csv_path)

    assert len(rows) == 1
    assert rows[0].scenario_id == "eurusd_m5_period_1"
    assert rows[0].conditions_evaluated == 55
    assert rows[0].low_sample_conditions_research == 47
    assert rows[0].source_file == str(csv_path)


def test_load_validation_summary_csv_defaults_missing_optional_columns(tmp_path: Path):
    csv_path = tmp_path / "summary.csv"
    pd.DataFrame(
        [{"Scenario_ID": "missing_optional", "Status": "COMPLETED", "Symbol": "EURUSD", "Timeframe": "H1"}]
    ).to_csv(csv_path, index=False)

    rows = load_validation_summary_csv(csv_path)

    assert rows[0].ohlc_rows == 0
    assert rows[0].average_structure_duration == 0.0
    assert rows[0].low_sample_conditions_price_outcome == 0


def test_load_validation_summaries_deduplicates_by_scenario_and_period(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    base = {
        "Scenario_ID": "eurusd_h1_period_1",
        "Status": "COMPLETED",
        "Symbol": "EURUSD",
        "Timeframe": "H1",
        "Period_Start": "2026-01-01",
        "Period_End": "2026-01-31",
    }
    pd.DataFrame([{**base, "OHLC_Rows": 100}]).to_csv(first, index=False)
    pd.DataFrame([{**base, "OHLC_Rows": 200}]).to_csv(second, index=False)

    rows = load_validation_summaries([first, second])

    assert len(rows) == 1
    assert rows[0].ohlc_rows == 200


def test_load_validation_summary_csv_raises_for_missing_file(tmp_path: Path):
    missing = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="Validation summary CSV not found"):
        load_validation_summary_csv(missing)
