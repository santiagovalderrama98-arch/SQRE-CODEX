#!/usr/bin/env python3
"""Run SQRE Phase 7.4.7 M15 introduction review."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.m15_introduction_review import M15IntroductionReviewConfig, run_m15_introduction_review


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE M15 introduction review")
    parser.add_argument("--m15-summary-csv", required=True, type=Path)
    parser.add_argument("--master-summary-csv", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--high-low-sample-threshold", type=int, default=50)
    parser.add_argument("--high-structure-cv-threshold", type=float, default=0.25)
    parser.add_argument("--duration-near-max-threshold", type=float, default=0.85)
    parser.add_argument("--high-state-diversity-threshold", type=int, default=7)
    parser.add_argument("--low-state-diversity-threshold", type=int, default=3)
    parser.add_argument("--forward-range-cv-threshold", type=float, default=0.25)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    config = M15IntroductionReviewConfig(
        high_low_sample_threshold=args.high_low_sample_threshold,
        high_structure_cv_threshold=args.high_structure_cv_threshold,
        duration_near_max_threshold=args.duration_near_max_threshold,
        high_state_diversity_threshold=args.high_state_diversity_threshold,
        low_state_diversity_threshold=args.low_state_diversity_threshold,
        forward_range_cv_threshold=args.forward_range_cv_threshold,
    )

    print("SQRE M15 introduction review started")
    print(f"M15 summary: {args.m15_summary_csv}")
    if args.master_summary_csv:
        print(f"Master summary: {args.master_summary_csv}")
    try:
        result = run_m15_introduction_review(
            m15_summary_csv=args.m15_summary_csv,
            master_summary_csv=args.master_summary_csv,
            output_path=args.output,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("M15 introduction review failed")
        print(f"M15 introduction review failed: {exc}")
        return 1

    print(f"Rows loaded: {result.rows_loaded}")
    print(f"Scenarios reviewed: {result.scenarios_reviewed}")
    print("M15 introduction review written:")
    print(f"- {result.output_path}")
    print(f"- {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
