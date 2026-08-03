#!/usr/bin/env python3
"""Run SQRE H4/D1 same-time alignment table generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_same_time_alignment_table import (  # noqa: E402
    H4D1SameTimeAlignmentConfig,
    run_h4_d1_same_time_alignment_table,
)


def parse_args() -> argparse.Namespace:
    defaults = H4D1SameTimeAlignmentConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 same-time alignment table generation")
    parser.add_argument("--timestamped-state-regime-dir", type=Path, default=defaults.timestamped_state_regime_dir)
    parser.add_argument("--synchronized-data-dir", type=Path, default=defaults.synchronized_data_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--h4-timeframe", default=defaults.h4_timeframe)
    parser.add_argument("--d1-timeframe", default=defaults.d1_timeframe)
    parser.add_argument("--minimum-transition-alignment-ratio", type=float, default=defaults.minimum_transition_alignment_ratio)
    parser.add_argument("--minimum-state-alignment-ratio", type=float, default=defaults.minimum_state_alignment_ratio)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4D1SameTimeAlignmentConfig(
        timestamped_state_regime_dir=args.timestamped_state_regime_dir,
        synchronized_data_dir=args.synchronized_data_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_transition_alignment_ratio=args.minimum_transition_alignment_ratio,
        minimum_state_alignment_ratio=args.minimum_state_alignment_ratio,
    )
    print(f"Timestamped state/regime directory: {config.timestamped_state_regime_dir}")
    print(f"Synchronized data directory: {config.synchronized_data_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_d1_same_time_alignment_table(config)
    except Exception as exc:
        print(f"H4/D1 same-time alignment table generation failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4/D1 same-time alignment table generation completed")
    print(f"H4 transition rows: {len(result.h4_transitions)}")
    print(f"H4 state rows: {len(result.h4_states)}")
    print(f"D1 state rows: {len(result.d1_states)}")
    if summary:
        print(f"Aligned H4 transition rows: {summary.aligned_h4_transition_row_count}")
        print(f"Unaligned H4 transition rows: {summary.unaligned_h4_transition_row_count}")
        print(f"Aligned H4 state rows: {summary.aligned_h4_state_row_count}")
        print(f"Unaligned H4 state rows: {summary.unaligned_h4_state_row_count}")
        print(f"Transition alignment ratio: {summary.transition_alignment_ratio}")
        print(f"State alignment ratio: {summary.state_alignment_ratio}")
        print(f"Dominant alignment coverage class: {summary.dominant_alignment_coverage_class}")
        print(f"H4/D1 same-time alignment readiness flag: {summary.h4_d1_same_time_alignment_readiness_flag}")
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {result.output_dir / 'h4_d1_same_time_alignment_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
