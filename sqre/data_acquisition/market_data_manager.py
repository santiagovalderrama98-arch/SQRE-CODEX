"""Provider-agnostic market data manager."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from sqre.data_acquisition.metadata import MetadataWriter
from sqre.data_acquisition.provider import MarketDataProvider
from sqre.data_acquisition.storage import MarketDataStorage
from sqre.data_acquisition.validation import DataValidator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MarketDataDownloadResult:
    provider: str
    symbol: str
    timeframe: str
    start_date: date
    end_date: date
    rows: int
    output_path: Path | None
    metadata_path: Path | None
    success: bool
    message: str


class MarketDataManager:
    """Coordinates provider download, normalization, validation and storage."""

    def __init__(
        self,
        providers: list[MarketDataProvider],
        *,
        storage: MarketDataStorage | None = None,
        validator: DataValidator | None = None,
        metadata_writer: MetadataWriter | None = None,
    ) -> None:
        self.providers = {provider.name.lower(): provider for provider in providers}
        self.storage = storage or MarketDataStorage()
        self.validator = validator or DataValidator()
        self.metadata_writer = metadata_writer or MetadataWriter()

    def download(
        self,
        *,
        provider_name: str,
        symbol: str,
        timeframe: str,
        start: date,
        end: date,
        output_path: Path | str | None = None,
        overwrite: bool = False,
    ) -> MarketDataDownloadResult:
        provider = self.providers.get(provider_name.lower())
        if provider is None:
            return self._failure(provider_name, symbol, timeframe, start, end, "Unknown provider")

        if not provider.supports(symbol, timeframe):
            return self._failure(
                provider.name,
                symbol,
                timeframe,
                start,
                end,
                f"Provider {provider.name} does not support {symbol} {timeframe}",
            )

        logger.info("Downloading market data with provider=%s symbol=%s timeframe=%s", provider.name, symbol, timeframe)
        try:
            raw_data = provider.download(symbol, timeframe, start, end)
            normalized = provider.normalize(raw_data)
            validation_summary = self.validator.validate(normalized)
            if not validation_summary["valid"]:
                return self._failure(
                    provider.name,
                    symbol,
                    timeframe,
                    start,
                    end,
                    f"Validation failed: {'; '.join(validation_summary['errors'])}",
                )

            saved_path = self.storage.save(
                normalized,
                symbol,
                timeframe,
                output_path=output_path,
                overwrite=overwrite,
            )
            metadata_path = self.metadata_writer.write(
                output_path=saved_path,
                provider=provider.name,
                symbol=symbol,
                timeframe=timeframe,
                start_date=start,
                end_date=end,
                rows=len(normalized),
                source="download",
                validation_summary=validation_summary,
            )
        except Exception as exc:
            logger.warning("Market data download failed: %s", exc)
            return self._failure(provider.name, symbol, timeframe, start, end, str(exc))

        return MarketDataDownloadResult(
            provider=provider.name,
            symbol=symbol.upper(),
            timeframe=timeframe.upper(),
            start_date=start,
            end_date=end,
            rows=len(normalized),
            output_path=saved_path,
            metadata_path=metadata_path,
            success=True,
            message="Market data downloaded and saved",
        )

    def _failure(
        self,
        provider: str,
        symbol: str,
        timeframe: str,
        start: date,
        end: date,
        message: str,
    ) -> MarketDataDownloadResult:
        return MarketDataDownloadResult(
            provider=provider,
            symbol=symbol.upper(),
            timeframe=timeframe.upper(),
            start_date=start,
            end_date=end,
            rows=0,
            output_path=None,
            metadata_path=None,
            success=False,
            message=message,
        )
