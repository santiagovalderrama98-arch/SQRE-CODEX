#!/usr/bin/env python3
"""Run H4/D1 same-time contextual transition review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_same_time_contextual_transition_review import (  # noqa: E402
    H4D1SameTimeContextualTransitionReviewConfig,
    H4D1SameTimeContextualTransitionReviewPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 same-time contextual transition review")
    parser.add_argument("--same-time-alignment-dir", type=Path, required=True)
    parser.add_argument("--timestamped-state-regime-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--minimum-context-sample-size", type=int, default=10)
    parser.add_argument("--minimum-transition-sample-size", type=int, default=20)
    parser.add_argument("--concentration-ratio-threshold", type=float, default=0.60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4D1SameTimeContextualTransitionReviewConfig(
        same_time_alignment_dir=args.same_time_alignment_dir,
        timestamped_state_regime_dir=args.timestamped_state_regime_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_context_sample_size=args.minimum_context_sample_size,
        minimum_transition_sample_size=args.minimum_transition_sample_size,
        concentration_ratio_threshold=args.concentration_ratio_threshold,
    )
    print(f"Same-time alignment directory: {config.same_time_alignment_dir}")
    print(f"Timestamped state/regime directory: {config.timestamped_state_regime_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    result = H4D1SameTimeContextualTransitionReviewPipeline(config).run()
    summary = result.summary
    print("H4/D1 same-time contextual transition review completed")
    if summary:
        print(f"Aligned H4 transition rows: {summary.aligned_h4_transition_row_count}")
        print(f"Distinct H4 transitions: {summary.distinct_h4_transition_count}")
        print(f"Distinct D1 market states: {summary.distinct_d1_market_state_count}")
        print(f"Distinct D1 regimes: {summary.distinct_d1_regime_count}")
        print(f"Context profiles: {summary.context_profile_count}")
        print(f"Research-ready contexts: {summary.research_ready_context_count}")
        print(
            "Low/insufficient contexts: "
            f"{summary.low_sample_context_count + summary.insufficient_context_count}"
        )
        print(f"Dominant contextual review class: {summary.dominant_contextual_review_class}")
        print(
            "H4/D1 contextual transition readiness flag: "
            f"{summary.h4_d1_contextual_transition_readiness_flag}"
        )
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {config.output_dir / 'h4_d1_same_time_contextual_transition_review_summary.csv'}")
    print(f"Report path: {config.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
