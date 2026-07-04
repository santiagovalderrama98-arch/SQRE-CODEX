"""Market data providers."""

from sqre.data_acquisition.providers.dukascopy_provider import DukascopyProvider
from sqre.data_acquisition.providers.histdata_provider import HistDataProvider
from sqre.data_acquisition.providers.mt5_provider import MT5Provider
from sqre.data_acquisition.providers.twelvedata_provider import TwelveDataProvider

__all__ = ["DukascopyProvider", "HistDataProvider", "MT5Provider", "TwelveDataProvider"]
