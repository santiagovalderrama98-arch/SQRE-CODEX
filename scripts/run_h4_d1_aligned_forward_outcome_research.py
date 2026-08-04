#!/usr/bin/env python3
"""Run H4/D1 aligned forward outcome research."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_aligned_forward_outcome_research import (  # noqa: E402
    H4D1AlignedForwardOutcomeResearchConfig,
    H4D1AlignedForwardOutcomeResearchPipeline,
    parse_forward_horizons,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 aligned forward outcome research")
    parser.add_argument("--same-time-alignment-dir", type=Path, required=True)
    parser.add_argument("--synchronized-data-dir", type=Path, required=True)
    parser.add_argument("--contextual-transition-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--forward-horizons", default="1,2,3,6,12")
    parser.add_argument("--minimum-outcome-sample-size", type=int, default=20)
    parser.add_argument("--minimum-context-outcome-sample-size", type=int, default=10)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4D1AlignedForwardOutcomeResearchConfig(
        same_time_alignment_dir=args.same_time_alignment_dir,
        synchronized_data_dir=args.synchronized_data_dir,
        contextual_transition_dir=args.contextual_transition_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        forward_horizons=parse_forward_horizons(args.forward_horizons),
        minimum_outcome_sample_size=args.minimum_outcome_sample_size,
        minimum_context_outcome_sample_size=args.minimum_context_outcome_sample_size,
    )
    print(f"Same-time alignment directory: {config.same_time_alignment_dir}")
    print(f"Synchronized data directory: {config.synchronized_data_dir}")
    print(f"Contextual transition directory: {config.contextual_transition_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    result = H4D1AlignedForwardOutcomeResearchPipeline(config).run()
    summary = result.summary
    print("H4/D1 aligned forward outcome research completed")
    if summary:
        print(f"Aligned H4 transition rows: {summary.aligned_h4_transition_row_count}")
        print(f"Forward outcome rows: {summary.forward_outcome_row_count}")
        print(f"Complete forward outcome rows: {summary.complete_forward_outcome_row_count}")
        print(f"Partial forward outcome rows: {summary.partial_forward_outcome_row_count}")
        print(f"Missing forward outcome rows: {summary.missing_forward_outcome_row_count}")
        print(f"Outcome profiles: {summary.outcome_profile_count}")
        print(f"Research-ready outcome profiles: {summary.research_ready_outcome_profile_count}")
        print(f"Moderate outcome profiles: {summary.moderate_outcome_profile_count}")
        print(f"Low/insufficient outcome profiles: {summary.low_or_insufficient_outcome_profile_count}")
        print(f"H4 transition only profiles: {summary.h4_transition_only_profile_count}")
        print(f"H4 transition + D1 market state profiles: {summary.h4_transition_d1_market_state_profile_count}")
        print(f"H4 transition + D1 regime profiles: {summary.h4_transition_d1_regime_profile_count}")
        print(f"H4 transition + D1 state/regime profiles: {summary.h4_transition_d1_state_regime_profile_count}")
        print(f"Dominant outcome readiness class: {summary.dominant_outcome_readiness_class}")
        print(f"H4/D1 aligned forward outcome readiness flag: {summary.h4_d1_aligned_forward_outcome_readiness_flag}")
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {config.output_dir / 'h4_d1_aligned_forward_outcome_research_summary.csv'}")
    print(f"Report path: {config.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
