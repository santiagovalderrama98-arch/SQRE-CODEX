#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.event_analytics.event_analytics_pipeline import EventAnalyticsPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE event analytics")
    parser.add_argument("--input", type=Path, default=Path("data/processed/events.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/reports"))
    parser.add_argument("--sequence-length", type=int, default=3)
    parser.add_argument("--pip-size", type=float, default=0.0001)
    parser.add_argument("--utc-offset-hours", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    print(f"Input events: {args.input}")
    print(f"Output directory: {args.output_dir}")

    result = EventAnalyticsPipeline().run(
        input_path=args.input,
        output_dir=args.output_dir,
        sequence_length=args.sequence_length,
        pip_size=args.pip_size,
        utc_offset_hours=args.utc_offset_hours,
    )

    if not result.success:
        print(f"Event analytics failed: {result.message}")
        return 1

    print("Event analytics completed")
    print(f"Rows processed: {result.rows_processed}")
    for name, path in result.outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
