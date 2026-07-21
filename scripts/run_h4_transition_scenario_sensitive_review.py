#!/usr/bin/env python3
"""Run SQRE H4 transition scenario-sensitive profile review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    run_h4_transition_scenario_sensitive_review,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4 transition scenario-sensitive profile review")
    parser.add_argument(
        "--dispersion-review-dir",
        type=Path,
        default=Path("data/research/h4_transition_scenario_dispersion_review"),
    )
    parser.add_argument(
        "--transition-deep-dive-dir",
        type=Path,
        default=Path("data/research/h4_transition_outcome_deep_dive"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/research/h4_transition_scenario_sensitive_review"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(
            "data/research/h4_transition_scenario_sensitive_review/"
            "h4_transition_scenario_sensitive_review_report.txt"
        ),
    )
    parser.add_argument("--moderate-deviation-threshold", type=float, default=0.20)
    parser.add_argument("--high-deviation-threshold", type=float, default=0.35)
    parser.add_argument("--near-candidate-high-deviation-max", type=int, default=1)
    parser.add_argument("--minimum-total-sample-size", type=int, default=20)
    parser.add_argument("--minimum-scenario-count", type=int, default=2)
    parser.add_argument(
        "--focus-transitions",
        default=(
            "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT,"
            "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION,"
            "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT,"
            "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    focus_transitions = tuple(item.strip().upper() for item in args.focus_transitions.split(",") if item.strip())
    config = H4TransitionScenarioSensitiveReviewConfig(
        moderate_deviation_threshold=args.moderate_deviation_threshold,
        high_deviation_threshold=args.high_deviation_threshold,
        near_candidate_high_deviation_max=args.near_candidate_high_deviation_max,
        minimum_total_sample_size=args.minimum_total_sample_size,
        minimum_scenario_count=args.minimum_scenario_count,
        focus_transitions=focus_transitions,
    )
    print(f"Dispersion review directory: {args.dispersion_review_dir}")
    print(f"Transition deep dive directory: {args.transition_deep_dive_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_h4_transition_scenario_sensitive_review(
            args.dispersion_review_dir,
            args.transition_deep_dive_dir,
            args.output_dir,
            args.report,
            config,
        )
    except Exception as exc:
        print(f"H4 transition scenario-sensitive review failed: {exc}", file=sys.stderr)
        return 1
    print("H4 transition scenario-sensitive review completed")
    print(f"Scenario-sensitive profiles loaded: {result.scenario_sensitive_profiles_loaded}")
    print(f"Profile review rows: {len(result.reviewed_profiles)}")
    print(f"Focus profile rows: {len(result.focus_profiles)}")
    print(f"Scenario deviation detail rows: {len(result.scenario_details)}")
    print(f"Scenario recurrent deviation rows: {len(result.scenario_summaries)}")
    print(f"Transition family sensitivity rows: {len(result.family_summaries)}")
    print(f"Source state sensitivity rows: {len(result.source_state_summaries)}")
    print(f"Target state sensitivity rows: {len(result.target_state_summaries)}")
    print(f"Forward window sensitivity rows: {len(result.window_summaries)}")
    print(f"Near aggregation candidate rows: {len(result.near_candidates)}")
    print(f"Summary path: {result.output_dir / 'h4_transition_scenario_sensitive_review_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
