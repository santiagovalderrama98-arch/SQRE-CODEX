#!/usr/bin/env python3
"""Run SQRE Phase 7.2 Price Outcome Research."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.price_outcome_research import PriceOutcomeResearchConfig, run_price_outcome_research


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE price outcome research")
    parser.add_argument("--states", required=True, help="Input market states CSV path")
    parser.add_argument("--transitions", required=True, help="Input state transitions CSV path")
    parser.add_argument("--ohlc", required=True, help="Input OHLC CSV path")
    parser.add_argument("--output-dir", required=True, help="Output directory for price outcome CSV files")
    parser.add_argument("--report", required=True, help="Output price outcome report path")
    parser.add_argument("--pip-size", type=float, default=0.0001)
    parser.add_argument("--forward-candles", default="3,6,12")
    parser.add_argument("--minimum-sample-size", type=int, default=5)
    parser.add_argument("--strong-negative-threshold-pips", type=float, default=-20.0)
    parser.add_argument("--moderate-negative-threshold-pips", type=float, default=-5.0)
    parser.add_argument("--moderate-positive-threshold-pips", type=float, default=5.0)
    parser.add_argument("--strong-positive-threshold-pips", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = PriceOutcomeResearchConfig(
        forward_candles=_parse_forward_candles(args.forward_candles),
        minimum_sample_size=args.minimum_sample_size,
        pip_size=args.pip_size,
        strong_negative_threshold_pips=args.strong_negative_threshold_pips,
        moderate_negative_threshold_pips=args.moderate_negative_threshold_pips,
        moderate_positive_threshold_pips=args.moderate_positive_threshold_pips,
        strong_positive_threshold_pips=args.strong_positive_threshold_pips,
    )

    try:
        summary = run_price_outcome_research(
            states_path=args.states,
            transitions_path=args.transitions,
            ohlc_path=args.ohlc,
            output_dir=args.output_dir,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("Price outcome research failed")
        print(f"Price outcome research failed: {exc}")
        return 1

    print("Price outcome research completed")
    print(f"Conditions evaluated: {summary.conditions_evaluated}")
    print(f"Price outcomes generated: {summary.price_outcomes_generated}")
    print(f"Summary rows: {summary.summary_rows}")
    print(f"Distribution rows: {summary.distribution_rows}")
    print(f"Price outcomes path: {summary.price_outcomes_path}")
    print(f"Condition price outcome summary path: {summary.condition_price_outcome_summary_path}")
    print(f"Price outcome distributions path: {summary.price_outcome_distributions_path}")
    print(f"Report path: {summary.report_path}")
    return 0


def _parse_forward_candles(value: str) -> list[int]:
    candles = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not candles:
        raise ValueError("--forward-candles must include at least one integer")
    if any(item <= 0 for item in candles):
        raise ValueError("--forward-candles values must be greater than zero")
    return candles


if __name__ == "__main__":
    raise SystemExit(main())
