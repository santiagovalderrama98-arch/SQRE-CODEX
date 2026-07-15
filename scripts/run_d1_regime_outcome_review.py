#!/usr/bin/env python3
"""Run D1 regime outcome dispersion and sample adequacy review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.d1_regime_outcome_review_pipeline import run_d1_regime_outcome_review


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE D1 regime outcome review")
    parser.add_argument(
        "--input-dir",
        default="data/research/d1_regime_normalized_research",
        help="Directory containing D1 regime-normalized research outputs",
    )
    parser.add_argument(
        "--output-dir",
        default="data/research/d1_regime_outcome_review",
        help="Directory for review CSV outputs",
    )
    parser.add_argument(
        "--report",
        default="data/research/d1_regime_outcome_review/d1_regime_outcome_review_report.txt",
        help="Text report path",
    )
    parser.add_argument("--minimum-total-sample-size", type=int, default=20)
    parser.add_argument("--minimum-regime-count", type=int, default=2)
    parser.add_argument("--full-regime-count", type=int, default=4)
    parser.add_argument("--moderate-dispersion-threshold", type=float, default=0.20)
    parser.add_argument("--high-dispersion-threshold", type=float, default=0.35)
    parser.add_argument("--moderate-sensitivity-threshold", type=float, default=0.20)
    parser.add_argument("--high-sensitivity-threshold", type=float, default=0.35)
    parser.add_argument("--low-sample-share-threshold", type=float, default=0.50)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = D1RegimeOutcomeReviewConfig(
        minimum_total_sample_size=args.minimum_total_sample_size,
        minimum_regime_count=args.minimum_regime_count,
        full_regime_count=args.full_regime_count,
        moderate_dispersion_threshold=args.moderate_dispersion_threshold,
        high_dispersion_threshold=args.high_dispersion_threshold,
        moderate_sensitivity_threshold=args.moderate_sensitivity_threshold,
        high_sensitivity_threshold=args.high_sensitivity_threshold,
        low_sample_share_threshold=args.low_sample_share_threshold,
    )

    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_d1_regime_outcome_review(args.input_dir, args.output_dir, args.report, config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"D1 regime outcome review failed: {exc}")
        return 1

    summary = result.review_summary
    print("D1 regime outcome review completed")
    print(f"Profiles loaded: {result.profiles_loaded}")
    print(f"Research-ready profiles: {len(result.research_ready_profiles)}")
    print(f"Regime-sensitive profiles: {len(result.regime_sensitive_profiles)}")
    print(f"Low-sample profiles: {len(result.low_sample_profiles)}")
    print(f"Limited-coverage profiles: {len(result.limited_coverage_profiles)}")
    if summary:
        print(f"Diagnostic: {summary.d1_outcome_review_diagnostic}")
    print(f"Summary path: {Path(args.output_dir) / 'd1_regime_outcome_review_summary.csv'}")
    print(f"Report path: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
