from __future__ import annotations

from datetime import date

from sqre.data_acquisition.market_data_manager import MarketDataManager
from sqre.data_acquisition.provider import MarketDataProvider
from sqre.data_acquisition.providers.histdata_provider import HistDataProvider
from sqre.data_acquisition.storage import MarketDataStorage


def test_provider_interface_runtime_check() -> None:
    assert isinstance(HistDataProvider(), MarketDataProvider)


def test_manager_returns_graceful_failure_when_provider_cannot_download(tmp_path) -> None:
    manager = MarketDataManager(
        [HistDataProvider()],
        storage=MarketDataStorage(tmp_path),
    )

    result = manager.download(
        provider_name="histdata",
        symbol="EURUSD",
        timeframe="M1",
        start=date(2020, 1, 1),
        end=date(2020, 1, 2),
    )

    assert not result.success
    assert result.output_path is None
    assert "manual" in result.message.lower()
