from pathlib import Path

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.loader import (
    load_csv_source,
    load_yaml_source,
    number_value,
    text_value,
)


def test_load_csv_source_counts_h4_rows(tmp_path: Path):
    path = tmp_path / "summary.csv"
    path.write_text("Scenario_ID,Timeframe\none,H4\ntwo,D1\nthree,H4\n", encoding="utf-8")

    frame, source = load_csv_source(path, "summary", "csv_summary")

    assert len(frame) == 3
    assert source.exists == "YES"
    assert source.load_status == "present_loaded"
    assert source.h4_rows_loaded == 2


def test_load_yaml_source_counts_h4_entries(tmp_path: Path):
    path = tmp_path / "samples.yaml"
    path.write_text(
        """
samples:
  - sample_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
  - sample_id: eurusd_d1_period_1
    symbol: EURUSD
    timeframe: D1
""",
        encoding="utf-8",
    )

    data, source = load_yaml_source(path, "samples")

    assert data
    assert source.rows_loaded == 2
    assert source.h4_rows_loaded == 1


def test_value_helpers_resolve_columns_case_insensitively():
    row = pd.Series({"Coverage_Ratio": "0.75", "scenario_id": "eurusd_h4_period_1"})

    assert text_value(row, "Scenario_ID") == "eurusd_h4_period_1"
    assert number_value(row, "coverage_ratio") == 0.75


def test_load_missing_csv_source_is_optional(tmp_path: Path):
    frame, source = load_csv_source(tmp_path / "missing.csv", "missing", "csv_summary")

    assert frame.empty
    assert source.exists == "NO"
    assert source.load_status == "missing_optional"
