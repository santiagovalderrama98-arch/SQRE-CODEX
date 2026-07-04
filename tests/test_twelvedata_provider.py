import json
from datetime import date
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import pytest

from sqre.data_acquisition.providers.twelvedata_provider import TwelveDataProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_supports_mapped_symbols_and_timeframes():
    provider = TwelveDataProvider(api_key="test-key")

    assert provider.supports("EURUSD", "M5")
    assert provider.supports("usdchf", "h4")
    assert not provider.supports("USDMXN", "M5")
    assert not provider.supports("EURUSD", "M2")


def test_download_maps_request_and_normalizes_response(monkeypatch):
    captured = {}

    def fake_urlopen(url, timeout):
        captured["url"] = url
        captured["timeout"] = str(timeout)
        return FakeResponse(
            {
                "status": "ok",
                "values": [
                    {
                        "datetime": "2020-01-01 00:00:00",
                        "open": "1.1000",
                        "high": "1.1010",
                        "low": "1.0990",
                        "close": "1.1005",
                        "volume": "42",
                    }
                ],
            }
        )

    monkeypatch.setattr("sqre.data_acquisition.providers.twelvedata_provider.urlopen", fake_urlopen)

    provider = TwelveDataProvider(api_key="test-key")
    raw = provider.download("EURUSD", "M5", date(2020, 1, 1), date(2020, 1, 31))
    normalized = provider.normalize(raw)

    query = parse_qs(urlparse(captured["url"]).query)
    assert query["symbol"] == ["EUR/USD"]
    assert query["interval"] == ["5min"]
    assert query["start_date"] == ["2020-01-01"]
    assert query["end_date"] == ["2020-01-31"]
    assert query["apikey"] == ["test-key"]
    assert captured["timeout"] == "30"
    assert len(normalized) == 1
    assert list(normalized.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert normalized.iloc[0]["Volume"] == 42


def test_download_sets_missing_volume_to_zero(monkeypatch):
    def fake_urlopen(url, timeout):
        return FakeResponse(
            {
                "values": [
                    {
                        "datetime": "2020-01-01",
                        "open": "1.0",
                        "high": "1.2",
                        "low": "0.9",
                        "close": "1.1",
                    }
                ]
            }
        )

    monkeypatch.setattr("sqre.data_acquisition.providers.twelvedata_provider.urlopen", fake_urlopen)

    provider = TwelveDataProvider(api_key="test-key")
    normalized = provider.normalize(provider.download("GBPUSD", "D1", date(2020, 1, 1), date(2020, 1, 2)))

    assert normalized.iloc[0]["Volume"] == 0


def test_download_fails_when_api_key_is_missing(monkeypatch):
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    provider = TwelveDataProvider()

    with pytest.raises(RuntimeError, match="TWELVE_DATA_API_KEY"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))


def test_download_fails_on_api_error(monkeypatch):
    def fake_urlopen(url, timeout):
        return FakeResponse({"status": "error", "message": "Invalid API key", "code": 401})

    monkeypatch.setattr("sqre.data_acquisition.providers.twelvedata_provider.urlopen", fake_urlopen)
    provider = TwelveDataProvider(api_key="bad-key")

    with pytest.raises(RuntimeError, match="Invalid API key"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))


def test_download_fails_on_api_limit(monkeypatch):
    def fake_urlopen(url, timeout):
        raise HTTPError(url, 429, "Too Many Requests", hdrs=None, fp=None)

    monkeypatch.setattr("sqre.data_acquisition.providers.twelvedata_provider.urlopen", fake_urlopen)
    provider = TwelveDataProvider(api_key="test-key")

    with pytest.raises(RuntimeError, match="limit"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))


def test_download_fails_when_no_data_is_returned(monkeypatch):
    def fake_urlopen(url, timeout):
        return FakeResponse({"status": "ok", "values": []})

    monkeypatch.setattr("sqre.data_acquisition.providers.twelvedata_provider.urlopen", fake_urlopen)
    provider = TwelveDataProvider(api_key="test-key")

    with pytest.raises(RuntimeError, match="no data"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))
