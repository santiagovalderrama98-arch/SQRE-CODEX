"""Storage helpers for standardized market data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class MarketDataStorage:
    """Persist SQRE market data CSV files without accidental overwrite."""

    def __init__(self, base_dir: Path | str = Path("data/raw")) -> None:
        self.base_dir = Path(base_dir)

    def target_path(self, symbol: str, timeframe: str) -> Path:
        return self.base_dir / f"{symbol.upper()}_{timeframe.upper()}.csv"

    def save(
        self,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        *,
        output_path: Path | str | None = None,
        overwrite: bool = False,
    ) -> Path:
        path = Path(output_path) if output_path else self.target_path(symbol, timeframe)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            raise FileExistsError(f"Output already exists: {path}. Use overwrite=True.")

        temp_path = path.with_suffix(path.suffix + ".tmp")
        data.to_csv(temp_path, index=False)
        temp_path.replace(path)
        return path
