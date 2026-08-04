#!/usr/bin/env python3
"""Run D1 regime context adequacy review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.d1_regime_context_adequacy_review import (  # noqa: E402
    D1RegimeContextAdequacyPipeline,
    D1RegimeContextAdequacyReviewConfig,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE D1 regime context adequacy review")
    parser.add_argument("--contextual-transition-dir", type=Path, required=True)
    parser.add_argument("--same-time-alignment-dir", type=Path, required=True)
    parser.add_argument("--timestamped-state-regime-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--minimum-context-sample-size", type=int, default=10)
    parser.add_argument("--minimum-transition-sample-size", type=int, default=20)
    parser.add_argument("--fragmentation-ratio-threshold", type=float, default=0.70)
    parser.add_argument("--dominant-context-share-threshold", type=float, default=0.60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = D1RegimeContextAdequacyReviewConfig(
        contextual_transition_dir=args.contextual_transition_dir,
        same_time_alignment_dir=args.same_time_alignment_dir,
        timestamped_state_regime_dir=args.timestamped_state_regime_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_context_sample_size=args.minimum_context_sample_size,
        minimum_transition_sample_size=args.minimum_transition_sample_size,
        fragmentation_ratio_threshold=args.fragmentation_ratio_threshold,
        dominant_context_share_threshold=args.dominant_context_share_threshold,
    )
    print(f"Contextual transition directory: {config.contextual_transition_dir}")
    print(f"Same-time alignment directory: {config.same_time_alignment_dir}")
    print(f"Timestamped state/regime directory: {config.timestamped_state_regime_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    result = D1RegimeContextAdequacyPipeline(config).run()
    summary = result.summary
    print("D1 regime context adequacy review completed")
    if summary:
        print(f"Aligned H4 transition rows: {summary.aligned_h4_transition_row_count}")
        print(f"Context profiles: {summary.context_profile_count}")
        print(f"Research-ready contexts: {summary.research_ready_context_count}")
        print(f"Low/insufficient contexts: {summary.low_or_insufficient_context_count}")
        print(f"D1 context count: {summary.d1_context_count}")
        print(f"High fragmentation transitions: {summary.high_fragmentation_transition_count}")
        print(f"Extreme fragmentation transitions: {summary.extreme_fragmentation_transition_count}")
        print(
            "High/extreme sample loss transitions: "
            f"{summary.high_sample_loss_transition_count + summary.extreme_sample_loss_transition_count}"
        )
        print(f"Aggregation candidates: {summary.aggregation_candidate_count}")
        print(f"Dominant D1 context adequacy class: {summary.dominant_d1_context_adequacy_class}")
        print(f"D1 regime context adequacy readiness flag: {summary.d1_regime_context_adequacy_readiness_flag}")
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {config.output_dir / 'd1_regime_context_adequacy_review_summary.csv'}")
    print(f"Report path: {config.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
