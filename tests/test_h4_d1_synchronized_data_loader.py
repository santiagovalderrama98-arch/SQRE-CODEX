from pathlib import Path

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.loader import normalize_h4_ohlc, read_optional_csv


def test_read_optional_csv_returns_empty_for_missing_file(tmp_path: Path):
    frame = read_optional_csv(tmp_path / "missing.csv")

    assert frame.empty


def test_normalize_h4_ohlc_supports_aliases_and_missing_volume(tmp_path: Path):
    path = tmp_path / "EURUSD_H4.csv"
    pd.DataFrame(
        {
            "Timestamp": ["2026-07-01 04:00:00", "2026-07-01 00:00:00"],
            "open": [1.2, 1.1],
            "high": [1.3, 1.2],
            "low": [1.1, 1.0],
            "close": [1.25, 1.15],
        }
    ).to_csv(path, index=False)

    result = normalize_h4_ohlc(path, "EURUSD")

    assert result.valid is True
    assert result.normalized_row_count == 2
    assert list(result.frame["Date"]) == ["2026-07-01 00:00:00", "2026-07-01 04:00:00"]
    assert result.frame["Volume"].tolist() == [0, 0]
    assert "Volume was missing" in result.diagnostic


def test_normalize_h4_ohlc_flags_conflicting_duplicate_timestamps(tmp_path: Path):
    path = tmp_path / "EURUSD_H4.csv"
    pd.DataFrame(
        {
            "Date": ["2026-07-01 00:00:00", "2026-07-01 00:00:00"],
            "Open": [1.1, 1.2],
            "High": [1.2, 1.3],
            "Low": [1.0, 1.1],
            "Close": [1.15, 1.25],
            "Volume": [10, 10],
        }
    ).to_csv(path, index=False)

    result = normalize_h4_ohlc(path, "EURUSD")

    assert result.valid is False
    assert result.conflicting_duplicate_timestamp_count == 2
    assert "conflicting OHLC" in result.diagnostic
