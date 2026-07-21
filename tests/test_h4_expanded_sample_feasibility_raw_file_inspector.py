from pathlib import Path

from sqre.h4_expanded_sample_feasibility_review.raw_file_inspector import (
    inspect_h4_raw_files,
    inspect_raw_file,
    scenario_id_from_raw_file,
)


def test_inspect_raw_file_extracts_h4_date_coverage(tmp_path: Path):
    path = tmp_path / "EURUSD_H4_period_1.csv"
    path.write_text(
        "Date,Open,High,Low,Close,Volume\n"
        "2020-01-01 00:00:00,1,2,0.5,1.5,0\n"
        "2020-01-02 00:00:00,1,2,0.5,1.5,0\n",
        encoding="utf-8",
    )

    row = inspect_raw_file(path)

    assert row.symbol == "EURUSD"
    assert row.timeframe == "H4"
    assert row.row_count == 2
    assert row.first_date == "2020-01-01"
    assert row.last_date == "2020-01-02"
    assert row.date_coverage_status == "KNOWN"
    assert scenario_id_from_raw_file(row) == "eurusd_h4_period_1"


def test_inspect_raw_file_handles_missing_date_column(tmp_path: Path):
    path = tmp_path / "EURUSD_H4_period_2.csv"
    path.write_text("Open,High,Low,Close\n1,2,0.5,1.5\n", encoding="utf-8")

    row = inspect_raw_file(path)

    assert row.row_count == 1
    assert row.date_coverage_status == "UNKNOWN"


def test_inspect_h4_raw_files_includes_partial_directory(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    partial_dir = raw_dir / "partial"
    raw_dir.mkdir()
    partial_dir.mkdir()
    (raw_dir / "EURUSD_H4_period_1.csv").write_text("Date\n2020-01-01\n", encoding="utf-8")
    (partial_dir / "EURUSD_H4_period_2.csv").write_text("Date\n2020-02-01\n", encoding="utf-8")

    rows = inspect_h4_raw_files(raw_dir, partial_dir)

    assert [row.partial_file_flag for row in rows] == ["NO", "YES"]
