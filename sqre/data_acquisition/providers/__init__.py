"""Market data providers."""

from sqre.data_acquisition.providers.dukascopy_provider import DukascopyProvider
from sqre.data_acquisition.providers.histdata_provider import HistDataProvider

__all__ = ["DukascopyProvider", "HistDataProvider"]
