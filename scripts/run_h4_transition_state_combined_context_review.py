#!/usr/bin/env python3
"""Run SQRE H4 transition/state combined context review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_transition_state_combined_context_review import (  # noqa: E402
    H4TransitionStateCombinedContextReviewConfig,
    run_h4_transition_state_combined_context_review,
)


def parse_args() -> argparse.Namespace:
    defaults = H4TransitionStateCombinedContextReviewConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4 transition/state combined context review")
    parser.add_argument("--h4-state-deep-dive-dir", type=Path, default=defaults.h4_state_deep_dive_dir)
    parser.add_argument("--h4-state-dispersion-dir", type=Path, default=defaults.h4_state_dispersion_dir)
    parser.add_argument("--h4-state-sensitive-dir", type=Path, default=defaults.h4_state_sensitive_dir)
    parser.add_argument("--h4-transition-deep-dive-dir", type=Path, default=defaults.h4_transition_deep_dive_dir)
    parser.add_argument("--h4-transition-dispersion-dir", type=Path, default=defaults.h4_transition_dispersion_dir)
    parser.add_argument("--h4-transition-sensitive-dir", type=Path, default=defaults.h4_transition_sensitive_dir)
    parser.add_argument("--partial-complement-dir", type=Path, default=defaults.partial_complement_dir)
    parser.add_argument("--partial-validation-dir", type=Path, default=defaults.partial_validation_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--timeframe", default=defaults.timeframe)
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--partial-sample-label", default=defaults.partial_sample_label)
    parser.add_argument("--baseline-scenario-count", type=int, default=defaults.baseline_scenario_count)
    parser.add_argument("--minimum-transition-sample-size", type=int, default=defaults.minimum_transition_sample_size)
    parser.add_argument("--minimum-state-sample-size", type=int, default=defaults.minimum_state_sample_size)
    parser.add_argument("--minimum-condition-profile-count", type=int, default=defaults.minimum_condition_profile_count)
    parser.add_argument("--scenario-sensitive-threshold", default=defaults.scenario_sensitive_threshold)
    parser.add_argument("--allow-partial-context", action=argparse.BooleanOptionalAction, default=defaults.allow_partial_context)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=args.h4_state_deep_dive_dir,
        h4_state_dispersion_dir=args.h4_state_dispersion_dir,
        h4_state_sensitive_dir=args.h4_state_sensitive_dir,
        h4_transition_deep_dive_dir=args.h4_transition_deep_dive_dir,
        h4_transition_dispersion_dir=args.h4_transition_dispersion_dir,
        h4_transition_sensitive_dir=args.h4_transition_sensitive_dir,
        partial_complement_dir=args.partial_complement_dir,
        partial_validation_dir=args.partial_validation_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        timeframe=args.timeframe,
        symbol=args.symbol,
        partial_sample_label=args.partial_sample_label,
        baseline_scenario_count=args.baseline_scenario_count,
        minimum_transition_sample_size=args.minimum_transition_sample_size,
        minimum_state_sample_size=args.minimum_state_sample_size,
        minimum_condition_profile_count=args.minimum_condition_profile_count,
        scenario_sensitive_threshold=args.scenario_sensitive_threshold,
        allow_partial_context=args.allow_partial_context,
    )
    print(f"State deep dive directory: {config.h4_state_deep_dive_dir}")
    print(f"Transition deep dive directory: {config.h4_transition_deep_dive_dir}")
    print(f"Partial context directory: {config.partial_complement_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_transition_state_combined_context_review(config)
    except Exception as exc:
        print(f"H4 transition/state combined context review failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4 transition/state combined context review completed")
    print(f"Source rows: {len(result.source_inventory)}")
    print(f"Context rows: {len(result.context_inventory)}")
    if summary:
        print(f"Readiness flag: {summary.h4_transition_state_context_readiness_flag}")
        print(f"Dominant interpretation: {summary.dominant_combined_context_interpretation}")
    print(f"Summary path: {result.output_dir / 'h4_transition_state_combined_context_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
