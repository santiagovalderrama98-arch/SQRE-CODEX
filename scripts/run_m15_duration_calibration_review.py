#!/usr/bin/env python3
"""Run SQRE Phase 7.4.8 M15 duration calibration review."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.m15_duration_calibration_review import (
    M15DurationCalibrationReviewConfig,
    run_m15_duration_calibration_review,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE M15 duration calibration review")
    parser.add_argument("--experiment-summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--baseline-profile", default="m15_duration_8h_baseline")
    parser.add_argument("--high-low-sample-threshold", type=int, default=50)
    parser.add_argument("--high-structure-cv-threshold", type=float, default=0.25)
    parser.add_argument("--duration-near-max-threshold", type=float, default=0.85)
    parser.add_argument("--fragmentation-increase-threshold", type=float, default=0.25)
    parser.add_argument("--compression-decrease-threshold", type=float, default=0.25)
    parser.add_argument("--high-state-diversity-threshold", type=int, default=7)
    parser.add_argument("--low-state-diversity-threshold", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    config = M15DurationCalibrationReviewConfig(
        baseline_profile=args.baseline_profile,
        high_low_sample_threshold=args.high_low_sample_threshold,
        high_structure_cv_threshold=args.high_structure_cv_threshold,
        duration_near_max_threshold=args.duration_near_max_threshold,
        fragmentation_increase_threshold=args.fragmentation_increase_threshold,
        compression_decrease_threshold=args.compression_decrease_threshold,
        high_state_diversity_threshold=args.high_state_diversity_threshold,
        low_state_diversity_threshold=args.low_state_diversity_threshold,
    )

    print("SQRE M15 duration calibration review started")
    print(f"Experiment summary: {args.experiment_summary}")
    try:
        result = run_m15_duration_calibration_review(
            experiment_summary_path=args.experiment_summary,
            output_path=args.output,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("M15 duration calibration review failed")
        print(f"M15 duration calibration review failed: {exc}")
        return 1

    print(f"Rows loaded: {result.rows_loaded}")
    print(f"Profiles reviewed: {result.profiles_reviewed}")
    print("M15 duration calibration review written:")
    print(f"- {result.output_path}")
    print(f"- {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
