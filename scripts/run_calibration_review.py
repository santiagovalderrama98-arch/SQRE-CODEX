#!/usr/bin/env python3
"""Run SQRE Phase 7.4 calibration review."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.calibration_review import CalibrationReviewConfig, run_calibration_review


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE calibration review")
    parser.add_argument("--summary-csv", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--duration-near-max-threshold", type=float, default=0.85)
    parser.add_argument("--state-dominance-threshold", type=float, default=0.60)
    parser.add_argument("--low-state-diversity-threshold", type=int, default=4)
    parser.add_argument("--low-sample-rate-threshold", type=float, default=0.50)
    parser.add_argument("--high-directional-ratio-threshold", type=float, default=0.75)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    config = CalibrationReviewConfig(
        duration_near_max_threshold=args.duration_near_max_threshold,
        state_dominance_threshold=args.state_dominance_threshold,
        low_state_diversity_threshold=args.low_state_diversity_threshold,
        low_sample_rate_threshold=args.low_sample_rate_threshold,
        high_directional_ratio_threshold=args.high_directional_ratio_threshold,
    )
    print("SQRE calibration review started")
    print(f"Input summaries: {len(args.summary_csv)}")
    try:
        summary = run_calibration_review(
            summary_csv_paths=args.summary_csv,
            output_path=args.output,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("Calibration review failed")
        print(f"Calibration review failed: {exc}")
        return 1

    print(f"Scenarios loaded: {summary.scenarios_loaded}")
    print(f"Calibration summary rows: {summary.summary_rows}")
    print(f"Calibration findings: {summary.finding_count}")
    print("Calibration review written:")
    print(f"- {summary.output_path}")
    print(f"- {summary.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
