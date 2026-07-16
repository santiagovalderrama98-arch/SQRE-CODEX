#!/usr/bin/env python3
"""Run SQRE H4 scenario dispersion review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_scenario_dispersion_review.config import H4ScenarioDispersionReviewConfig
from sqre.h4_scenario_dispersion_review.h4_scenario_dispersion_review_pipeline import (
    run_h4_scenario_dispersion_review,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4 scenario dispersion review")
    parser.add_argument("--input-dir", type=Path, default=Path("data/research/h4_state_outcome_deep_dive"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/research/h4_scenario_dispersion_review"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/research/h4_scenario_dispersion_review/h4_scenario_dispersion_review_report.txt"),
    )
    parser.add_argument("--moderate-deviation-threshold", type=float, default=0.20)
    parser.add_argument("--high-deviation-threshold", type=float, default=0.35)
    parser.add_argument("--moderate-dispersion-threshold", type=float, default=0.20)
    parser.add_argument("--high-dispersion-threshold", type=float, default=0.35)
    parser.add_argument("--minimum-total-sample-size", type=int, default=20)
    parser.add_argument("--minimum-scenario-count", type=int, default=2)
    parser.add_argument("--full-scenario-count", type=int, default=4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4ScenarioDispersionReviewConfig(
        moderate_deviation_threshold=args.moderate_deviation_threshold,
        high_deviation_threshold=args.high_deviation_threshold,
        moderate_dispersion_threshold=args.moderate_dispersion_threshold,
        high_dispersion_threshold=args.high_dispersion_threshold,
        minimum_total_sample_size=args.minimum_total_sample_size,
        minimum_scenario_count=args.minimum_scenario_count,
        full_scenario_count=args.full_scenario_count,
    )
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_h4_scenario_dispersion_review(args.input_dir, args.output_dir, args.report, config)
    except Exception as exc:
        print(f"H4 scenario dispersion review failed: {exc}", file=sys.stderr)
        return 1
    print("H4 scenario dispersion review completed")
    print(f"Input profiles loaded: {result.profiles_loaded}")
    print(f"Profile dispersion diagnostics: {len(result.profile_diagnostics)}")
    print(f"Scenario contribution rows: {len(result.scenario_contributions)}")
    print(f"State dispersion rows: {len(result.state_summaries)}")
    print(f"Forward window dispersion rows: {len(result.window_summaries)}")
    print(f"Aggregation candidate profiles: {len(result.aggregation_candidates)}")
    print(f"Scenario-sensitive profiles: {len(result.scenario_sensitive_profiles)}")
    print(f"Sample-constrained profiles: {len(result.sample_constrained_profiles)}")
    print(f"Summary path: {result.output_dir / 'h4_scenario_dispersion_review_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
