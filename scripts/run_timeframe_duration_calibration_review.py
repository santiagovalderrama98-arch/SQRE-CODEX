#!/usr/bin/env python3
"""Run SQRE Phase 7.4.6 H1/M5 duration calibration review."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.timeframe_duration_calibration_review import (
    TimeframeDurationCalibrationReviewConfig,
    run_timeframe_duration_calibration_review,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H1/M5 duration calibration review")
    parser.add_argument("--experiment-summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--baseline-profile-h1", default="h1_duration_24h_baseline")
    parser.add_argument("--baseline-profile-m5", default="m5_duration_4h_baseline")
    parser.add_argument("--high-low-sample-threshold", type=int, default=50)
    parser.add_argument("--high-structure-cv-threshold", type=float, default=0.25)
    parser.add_argument("--duration-near-max-threshold", type=float, default=0.85)
    parser.add_argument("--fragmentation-increase-threshold", type=float, default=0.25)
    parser.add_argument("--compression-decrease-threshold", type=float, default=0.25)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    config = TimeframeDurationCalibrationReviewConfig(
        baseline_profile_h1=args.baseline_profile_h1,
        baseline_profile_m5=args.baseline_profile_m5,
        high_low_sample_threshold=args.high_low_sample_threshold,
        high_structure_cv_threshold=args.high_structure_cv_threshold,
        duration_near_max_threshold=args.duration_near_max_threshold,
        fragmentation_increase_threshold=args.fragmentation_increase_threshold,
        compression_decrease_threshold=args.compression_decrease_threshold,
    )

    print("SQRE H1/M5 duration calibration review started")
    print(f"Experiment summary: {args.experiment_summary}")
    try:
        result = run_timeframe_duration_calibration_review(
            experiment_summary_path=args.experiment_summary,
            output_path=args.output,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("H1/M5 duration calibration review failed")
        print(f"H1/M5 duration calibration review failed: {exc}")
        return 1

    print(f"Rows loaded: {result.rows_loaded}")
    print(f"Timeframes reviewed: {result.timeframes_reviewed}")
    print(f"Profiles reviewed: {result.profiles_reviewed}")
    print("H1/M5 duration calibration review written:")
    print(f"- {result.output_path}")
    print(f"- {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
