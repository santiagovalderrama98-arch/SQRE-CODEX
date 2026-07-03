"""Metadata writing for SQRE market data artifacts."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


class MetadataWriter:
    """Writes sidecar JSON metadata for saved market data."""

    def metadata_path_for(self, output_path: Path | str) -> Path:
        path = Path(output_path)
        return path.with_suffix(".metadata.json")

    def write(
        self,
        *,
        output_path: Path | str,
        provider: str,
        symbol: str,
        timeframe: str,
        start_date: date,
        end_date: date,
        rows: int,
        source: str,
        validation_summary: dict[str, Any],
    ) -> Path:
        metadata_path = self.metadata_path_for(output_path)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "provider": provider,
            "symbol": symbol.upper(),
            "timeframe": timeframe.upper(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "rows": rows,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "validation_summary": validation_summary,
        }
        metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return metadata_path
