#!/usr/bin/env python3
"""Run SQRE Phase 7.4.4 expanded historical calibration review."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.expanded_calibration_review import ExpandedCalibrationReviewConfig, run_expanded_calibration_review


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE expanded historical calibration review")
    parser.add_argument("--summary-csv", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--min-scenarios-per-timeframe", type=int, default=2)
    parser.add_argument("--high-low-sample-threshold", type=int, default=50)
    parser.add_argument("--high-state-diversity-threshold", type=int, default=7)
    parser.add_argument("--low-state-diversity-threshold", type=int, default=3)
    parser.add_argument("--high-structure-variation-threshold", type=float, default=0.25)
    parser.add_argument("--high-forward-range-variation-threshold", type=float, default=0.35)
    parser.add_argument("--high-unclassified-rate-threshold", type=float, default=0.10)
    parser.add_argument("--high-low-quality-rate-threshold", type=float, default=0.10)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    config = ExpandedCalibrationReviewConfig(
        min_scenarios_per_timeframe=args.min_scenarios_per_timeframe,
        high_low_sample_threshold=args.high_low_sample_threshold,
        high_state_diversity_threshold=args.high_state_diversity_threshold,
        low_state_diversity_threshold=args.low_state_diversity_threshold,
        high_structure_variation_threshold=args.high_structure_variation_threshold,
        high_forward_range_variation_threshold=args.high_forward_range_variation_threshold,
        high_unclassified_rate_threshold=args.high_unclassified_rate_threshold,
        high_low_quality_rate_threshold=args.high_low_quality_rate_threshold,
    )
    print("SQRE expanded historical calibration review started")
    print(f"Input summaries: {len(args.summary_csv)}")
    try:
        summary = run_expanded_calibration_review(
            summary_csv_paths=args.summary_csv,
            output_path=args.output,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("Expanded historical calibration review failed")
        print(f"Expanded historical calibration review failed: {exc}")
        return 1

    print(f"Rows loaded: {summary.rows_loaded}")
    print(f"Timeframes reviewed: {summary.timeframes_reviewed}")
    print("Expanded historical calibration review written:")
    print(f"- {summary.output_path}")
    print(f"- {summary.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
