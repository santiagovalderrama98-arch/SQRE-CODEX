"""Lightweight OHLCV validation used by the acquisition manager."""

from __future__ import annotations

from typing import Any

import pandas as pd

from sqre.data_acquisition.normalizer import STANDARD_COLUMNS


class DataValidator:
    """Validate SQRE standard OHLCV data."""

    def validate(self, data: pd.DataFrame) -> dict[str, Any]:
        errors: list[str] = []
        missing = [column for column in STANDARD_COLUMNS if column not in data.columns]
        if missing:
            errors.append(f"Missing columns: {', '.join(missing)}")

        if data.empty:
            errors.append("Dataset is empty")

        if not missing and not data.empty:
            dates = pd.to_datetime(data["Date"], errors="coerce")
            if dates.isna().any():
                errors.append("Date column contains invalid values")
            if dates.duplicated().any():
                errors.append("Date column contains duplicates")
            if not dates.is_monotonic_increasing:
                errors.append("Date column is not sorted ascending")

            for column in ["Open", "High", "Low", "Close", "Volume"]:
                values = pd.to_numeric(data[column], errors="coerce")
                if values.isna().any():
                    errors.append(f"{column} contains non-numeric values")

            high = pd.to_numeric(data["High"], errors="coerce")
            low = pd.to_numeric(data["Low"], errors="coerce")
            if (high < low).any():
                errors.append("High contains values lower than Low")

        return {"valid": not errors, "errors": errors, "rows": int(len(data))}
