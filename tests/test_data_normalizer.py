from __future__ import annotations

import pandas as pd
from zipfile import ZipFile

from sqre.data_acquisition.normalizer import DataNormalizer, STANDARD_COLUMNS


def test_normalizes_already_standard_data() -> None:
    raw = pd.DataFrame(
        {
            "Date": ["2020-01-02", "2020-01-01"],
            "Open": [1.2, 1.1],
            "High": [1.3, 1.2],
            "Low": [1.1, 1.0],
            "Close": [1.25, 1.15],
            "Volume": [10, 20],
        }
    )

    normalized = DataNormalizer().normalize(raw)

    assert list(normalized.columns) == STANDARD_COLUMNS
    assert normalized.iloc[0]["Date"] == pd.Timestamp("2020-01-01")


def test_normalizes_generic_ohlc_aliases_without_volume() -> None:
    raw = pd.DataFrame(
        {
            "timestamp": ["2020-01-01 00:00:00"],
            "o": [1.0],
            "h": [1.1],
            "l": [0.9],
            "c": [1.05],
        }
    )

    normalized = DataNormalizer().normalize(raw)

    assert list(normalized.columns) == STANDARD_COLUMNS
    assert normalized.iloc[0]["Volume"] == 0


def test_normalizes_histdata_semicolon_csv(tmp_path) -> None:
    path = tmp_path / "DAT_ASCII_EURUSD_M1_2020.csv"
    path.write_text(
        "20200101 000000;1.1000;1.1010;1.0990;1.1005;0\n"
        "20200101 000100;1.1005;1.1020;1.1000;1.1015;0\n",
        encoding="utf-8",
    )

    normalized = DataNormalizer().from_csv(path)

    assert len(normalized) == 2
    assert list(normalized.columns) == STANDARD_COLUMNS
    assert normalized.iloc[0]["Open"] == 1.1


def test_detects_histdata_content_without_histdata_filename(tmp_path) -> None:
    path = tmp_path / "eurusd.csv"
    path.write_text("20200101 000000;1.1000;1.1010;1.0990;1.1005;0\n", encoding="utf-8")

    normalized = DataNormalizer().from_csv(path)

    assert len(normalized) == 1
    assert normalized.iloc[0]["Close"] == 1.1005


def test_normalizes_histdata_zip(tmp_path) -> None:
    path = tmp_path / "histdata.zip"
    with ZipFile(path, "w") as archive:
        archive.writestr("DAT_ASCII_EURUSD_M1_2020.csv", "20200101 000000;1.0;1.2;0.9;1.1;0\n")

    normalized = DataNormalizer().from_csv(path)

    assert len(normalized) == 1
    assert normalized.iloc[0]["High"] == 1.2
