#!/usr/bin/env python3
"""Run H4/D1 forward outcome interpretation review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_forward_outcome_interpretation_review import (  # noqa: E402
    H4D1ForwardOutcomeInterpretationReviewConfig,
    H4D1ForwardOutcomeInterpretationReviewPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 forward outcome interpretation review")
    parser.add_argument("--forward-outcome-dir", type=Path, required=True)
    parser.add_argument("--contextual-transition-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--minimum-interpretation-sample-size", type=int, default=20)
    parser.add_argument("--minimum-moderate-sample-size", type=int, default=10)
    parser.add_argument("--directional-imbalance-threshold", type=float, default=0.60)
    parser.add_argument("--strong-directional-imbalance-threshold", type=float, default=0.70)
    parser.add_argument("--high-dispersion-threshold-pips", type=float, default=40.0)
    parser.add_argument("--extreme-dispersion-threshold-pips", type=float, default=80.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4D1ForwardOutcomeInterpretationReviewConfig(
        forward_outcome_dir=args.forward_outcome_dir,
        contextual_transition_dir=args.contextual_transition_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_interpretation_sample_size=args.minimum_interpretation_sample_size,
        minimum_moderate_sample_size=args.minimum_moderate_sample_size,
        directional_imbalance_threshold=args.directional_imbalance_threshold,
        strong_directional_imbalance_threshold=args.strong_directional_imbalance_threshold,
        high_dispersion_threshold_pips=args.high_dispersion_threshold_pips,
        extreme_dispersion_threshold_pips=args.extreme_dispersion_threshold_pips,
    )
    print(f"Forward outcome directory: {config.forward_outcome_dir}")
    print(f"Contextual transition directory: {config.contextual_transition_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    result = H4D1ForwardOutcomeInterpretationReviewPipeline(config).run()
    summary = result.summary
    print("H4/D1 forward outcome interpretation review completed")
    if summary:
        print(f"Outcome profile count: {summary.outcome_profile_count}")
        print(f"Interpretable profile count: {summary.interpretable_profile_count}")
        print(f"Moderately interpretable profile count: {summary.moderately_interpretable_profile_count}")
        print(f"Low interpretability profile count: {summary.low_interpretability_profile_count}")
        print(f"Sample-constrained profile count: {summary.sample_constrained_profile_count}")
        print(f"High-dispersion profile count: {summary.high_dispersion_profile_count}")
        print(f"Upward dominance profile count: {summary.upward_dominance_profile_count}")
        print(f"Downward dominance profile count: {summary.downward_dominance_profile_count}")
        print(f"Mixed behavior profile count: {summary.mixed_behavior_profile_count}")
        print(f"Stable horizon context count: {summary.stable_horizon_context_count}")
        print(f"Unstable horizon context count: {summary.unstable_horizon_context_count}")
        print(f"Best-supported context granularity: {summary.best_supported_context_granularity}")
        print(f"Dominant interpretation readiness class: {summary.dominant_interpretation_readiness_class}")
        print(
            "H4/D1 forward outcome interpretation readiness flag: "
            f"{summary.h4_d1_forward_outcome_interpretation_readiness_flag}"
        )
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {config.output_dir / 'h4_d1_forward_outcome_interpretation_review_summary.csv'}")
    print(f"Report path: {config.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
