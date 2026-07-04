#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.event_engine.event_pipeline import EventPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE event detection")
    parser.add_argument("--input", type=Path, default=Path("data/raw/EURUSD_M5.csv"))
    parser.add_argument("--output-events", type=Path, default=Path("data/processed/events.csv"))
    parser.add_argument("--output-report", type=Path, default=Path("data/reports/event_report.txt"))
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--timeframe", default="M5")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    print(f"Input: {args.input}")
    print(f"Output events: {args.output_events}")
    print(f"Output report: {args.output_report}")

    result = EventPipeline().run(
        input_path=args.input,
        output_events=args.output_events,
        output_report=args.output_report,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )

    if not result.success:
        print(f"Event detection failed: {result.message}")
        return 1

    print("Event detection completed")
    print(f"Events saved: {result.events}")
    print(f"Events path: {result.events_path}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
