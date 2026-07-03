#!/usr/bin/env python3
"""Ingest a manually downloaded HistData CSV into SQRE standard format."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.data_acquisition.metadata import MetadataWriter
from sqre.data_acquisition.providers.histdata_provider import HistDataProvider
from sqre.data_acquisition.storage import MarketDataStorage
from sqre.data_acquisition.validation import DataValidator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest HistData CSV files")
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    provider = HistDataProvider()
    storage = MarketDataStorage()
    validator = DataValidator()
    metadata_writer = MetadataWriter()

    print(f"Provider selected: {provider.name}")
    print(f"Target: {args.symbol.upper()} {args.timeframe.upper()}")
    print(f"Input file: {args.file}")

    data = provider.ingest_file(args.file)
    validation_summary = validator.validate(data)
    if not validation_summary["valid"]:
        print(f"Validation result: invalid - {'; '.join(validation_summary['errors'])}")
        return 1

    output_path = storage.save(
        data,
        args.symbol,
        args.timeframe,
        output_path=args.output,
        overwrite=args.overwrite,
    )
    start_date = data["Date"].min().date()
    end_date = data["Date"].max().date()
    metadata_path = metadata_writer.write(
        output_path=output_path,
        provider=provider.name,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=date.fromisoformat(str(start_date)),
        end_date=date.fromisoformat(str(end_date)),
        rows=len(data),
        source=str(args.file),
        validation_summary=validation_summary,
    )

    print(f"Output path: {output_path}")
    print(f"Metadata path: {metadata_path}")
    print("Validation result: valid")
    print(f"Rows saved: {len(data)}")
    print("Next recommended command: python3 scripts/run_event_detection.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
