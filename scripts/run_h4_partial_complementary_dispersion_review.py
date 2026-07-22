#!/usr/bin/env python3
"""Run SQRE H4 partial sample complementary dispersion review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_partial_complementary_dispersion_review import (  # noqa: E402
    H4PartialComplementaryDispersionReviewConfig,
    run_h4_partial_complementary_dispersion_review,
)


def parse_args() -> argparse.Namespace:
    defaults = H4PartialComplementaryDispersionReviewConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4 partial sample complementary dispersion review")
    parser.add_argument("--partial-validation-dir", type=Path, default=defaults.partial_validation_dir)
    parser.add_argument("--h4-state-dispersion-dir", type=Path, default=defaults.h4_state_dispersion_dir)
    parser.add_argument("--h4-state-sensitive-dir", type=Path, default=defaults.h4_state_sensitive_dir)
    parser.add_argument("--h4-transition-dispersion-dir", type=Path, default=defaults.h4_transition_dispersion_dir)
    parser.add_argument("--h4-transition-sensitive-dir", type=Path, default=defaults.h4_transition_sensitive_dir)
    parser.add_argument("--h4-transition-deep-dive-dir", type=Path, default=defaults.h4_transition_deep_dive_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--candidate-id", default=defaults.candidate_id)
    parser.add_argument("--partial-sample-label", default=defaults.partial_sample_label)
    parser.add_argument("--baseline-scenario-count", type=int, default=defaults.baseline_scenario_count)
    parser.add_argument("--consistency-lower-bound", type=float, default=defaults.consistency_lower_bound)
    parser.add_argument("--consistency-upper-bound", type=float, default=defaults.consistency_upper_bound)
    parser.add_argument("--minimum-condition-profile-count", type=int, default=defaults.minimum_condition_profile_count)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4PartialComplementaryDispersionReviewConfig(
        partial_validation_dir=args.partial_validation_dir,
        h4_state_dispersion_dir=args.h4_state_dispersion_dir,
        h4_state_sensitive_dir=args.h4_state_sensitive_dir,
        h4_transition_dispersion_dir=args.h4_transition_dispersion_dir,
        h4_transition_sensitive_dir=args.h4_transition_sensitive_dir,
        h4_transition_deep_dive_dir=args.h4_transition_deep_dive_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        candidate_id=args.candidate_id,
        partial_sample_label=args.partial_sample_label,
        baseline_scenario_count=args.baseline_scenario_count,
        consistency_lower_bound=args.consistency_lower_bound,
        consistency_upper_bound=args.consistency_upper_bound,
        minimum_condition_profile_count=args.minimum_condition_profile_count,
    )
    print(f"Partial validation directory: {config.partial_validation_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_partial_complementary_dispersion_review(config)
    except Exception as exc:
        print(f"H4 partial complementary dispersion review failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4 partial complementary dispersion review completed")
    print(f"Source rows: {len(result.source_inventory)}")
    print(f"Reviewed partial samples: {len(result.partial_samples)}")
    if result.partial_samples:
        print(f"Partial candidate: {result.partial_samples[0].candidate_id}")
        print(f"Partial sample status: {result.partial_samples[0].partial_sample_status}")
    if summary:
        print(f"Readiness flag: {summary.h4_partial_complementary_readiness_flag}")
    print(f"Summary path: {result.output_dir / 'h4_partial_complementary_dispersion_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
