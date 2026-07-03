#!/usr/bin/env python3
"""Download market data through SQRE's provider-agnostic manager."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.data_acquisition.market_data_manager import MarketDataManager
from sqre.data_acquisition.providers import DukascopyProvider, HistDataProvider


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download SQRE market data")
    parser.add_argument("--provider", required=True, choices=["histdata", "dukascopy"])
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    manager = MarketDataManager([HistDataProvider(), DukascopyProvider()])
    print(f"Provider selected: {args.provider}")
    print(f"Target: {args.symbol.upper()} {args.timeframe.upper()}")

    result = manager.download(
        provider_name=args.provider,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start=args.start,
        end=args.end,
        output_path=args.output,
        overwrite=args.overwrite,
    )

    if not result.success:
        print(f"Download failed: {result.message}")
        print("Recommended manual ingestion:")
        print(
            "python3 scripts/ingest_histdata_file.py "
            "--file data/external/DAT_ASCII_EURUSD_M1_2020.csv "
            "--symbol EURUSD --timeframe M1"
        )
        return 1

    print(f"Output path: {result.output_path}")
    print(f"Metadata path: {result.metadata_path}")
    print("Validation result: valid")
    print(f"Rows saved: {result.rows}")
    print("Next recommended command: python3 scripts/run_event_detection.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
