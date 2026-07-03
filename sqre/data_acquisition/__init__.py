"""Provider-agnostic market data acquisition for SQRE."""

from sqre.data_acquisition.market_data_manager import (
    MarketDataDownloadResult,
    MarketDataManager,
)
from sqre.data_acquisition.provider import MarketDataProvider

__all__ = ["MarketDataDownloadResult", "MarketDataManager", "MarketDataProvider"]
