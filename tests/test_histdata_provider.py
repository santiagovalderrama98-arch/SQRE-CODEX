from __future__ import annotations

from datetime import date

import pytest

from sqre.data_acquisition.providers.histdata_provider import HistDataProvider


def test_histdata_provider_supports_common_timeframes() -> None:
    provider = HistDataProvider()

    assert provider.supports("EURUSD", "M1")
    assert not provider.supports("EURUSD", "TICK")


def test_histdata_provider_manual_ingestion(tmp_path) -> None:
    path = tmp_path / "DAT_ASCII_EURUSD_M1_2020.csv"
    path.write_text("20200101 000000;1.0;1.2;0.9;1.1;0\n", encoding="utf-8")

    data = HistDataProvider().ingest_file(path)

    assert len(data) == 1
    assert data.iloc[0]["Close"] == 1.1


def test_histdata_auto_download_fails_with_manual_ingestion_guidance() -> None:
    provider = HistDataProvider()

    with pytest.raises(RuntimeError, match="manual"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))
