#!/usr/bin/env python3
"""Run SQRE H4 scenario-sensitive state profile review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig
from sqre.h4_scenario_sensitive_state_review.h4_scenario_sensitive_state_review_pipeline import (
    run_h4_scenario_sensitive_state_review,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4 scenario-sensitive state profile review")
    parser.add_argument(
        "--dispersion-review-dir",
        type=Path,
        default=Path("data/research/h4_scenario_dispersion_review"),
    )
    parser.add_argument(
        "--state-deep-dive-dir",
        type=Path,
        default=Path("data/research/h4_state_outcome_deep_dive"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/research/h4_scenario_sensitive_state_review"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/research/h4_scenario_sensitive_state_review/h4_scenario_sensitive_state_review_report.txt"),
    )
    parser.add_argument("--moderate-deviation-threshold", type=float, default=0.20)
    parser.add_argument("--high-deviation-threshold", type=float, default=0.35)
    parser.add_argument("--near-candidate-high-deviation-max", type=int, default=1)
    parser.add_argument("--minimum-total-sample-size", type=int, default=20)
    parser.add_argument("--minimum-scenario-count", type=int, default=2)
    parser.add_argument(
        "--focus-states",
        default="DIRECTIONAL_DISPLACEMENT,DIRECTIONAL_EXPANSION,VOLATILE_ROTATION",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    focus_states = tuple(item.strip().upper() for item in args.focus_states.split(",") if item.strip())
    config = H4ScenarioSensitiveStateReviewConfig(
        moderate_deviation_threshold=args.moderate_deviation_threshold,
        high_deviation_threshold=args.high_deviation_threshold,
        near_candidate_high_deviation_max=args.near_candidate_high_deviation_max,
        minimum_total_sample_size=args.minimum_total_sample_size,
        minimum_scenario_count=args.minimum_scenario_count,
        focus_states=focus_states,
    )
    print(f"Dispersion review directory: {args.dispersion_review_dir}")
    print(f"State deep dive directory: {args.state_deep_dive_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_h4_scenario_sensitive_state_review(
            args.dispersion_review_dir,
            args.state_deep_dive_dir,
            args.output_dir,
            args.report,
            config,
        )
    except Exception as exc:
        print(f"H4 scenario-sensitive state review failed: {exc}", file=sys.stderr)
        return 1
    print("H4 scenario-sensitive state review completed")
    print(f"Scenario-sensitive profiles loaded: {result.scenario_sensitive_profiles_loaded}")
    print(f"Profile review rows: {len(result.reviewed_profiles)}")
    print(f"Scenario deviation detail rows: {len(result.scenario_details)}")
    print(f"Scenario recurrent deviation rows: {len(result.scenario_summaries)}")
    print(f"State sensitivity rows: {len(result.state_summaries)}")
    print(f"Forward window sensitivity rows: {len(result.window_summaries)}")
    print(f"Near aggregation candidate rows: {len(result.near_candidates)}")
    print(f"Summary path: {result.output_dir / 'h4_scenario_sensitive_state_review_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
