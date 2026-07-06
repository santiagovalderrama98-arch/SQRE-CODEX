#!/usr/bin/env python3
"""Run SQRE Phase 5 Market States."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.market_states import MarketStatesPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE market states classification")
    parser.add_argument("--structures", required=True, help="Input structures CSV path")
    parser.add_argument("--output", required=True, help="Output market states CSV path")
    parser.add_argument("--report", required=True, help="Output market states report path")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    print(f"Input structures: {args.structures}")
    print(f"Output states: {args.output}")
    print(f"Report: {args.report}")

    try:
        result = MarketStatesPipeline().run(
            structures_path=args.structures,
            output_path=args.output,
            report_path=args.report,
        )
    except Exception as exc:
        logging.exception("Market states failed")
        print(f"Market states failed: {exc}")
        return 1

    print(result.message)
    print(f"Structures processed: {result.structures_processed}")
    print(f"States generated: {result.states_generated}")
    print(f"Most common state: {result.most_common_state}")
    print(f"Market states path: {result.output_path}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
