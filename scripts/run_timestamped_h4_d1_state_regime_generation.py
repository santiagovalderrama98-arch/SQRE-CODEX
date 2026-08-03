#!/usr/bin/env python3
"""Run SQRE timestamped H4/D1 state and regime table generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.timestamped_h4_d1_state_regime_generation import (  # noqa: E402
    TimestampedH4D1StateRegimeGenerationConfig,
    run_timestamped_h4_d1_state_regime_generation,
)


def parse_args() -> argparse.Namespace:
    defaults = TimestampedH4D1StateRegimeGenerationConfig()
    parser = argparse.ArgumentParser(description="Run SQRE timestamped H4/D1 state and regime table generation")
    parser.add_argument("--synchronized-data-dir", type=Path, default=defaults.synchronized_data_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--h4-timeframe", default=defaults.h4_timeframe)
    parser.add_argument("--d1-timeframe", default=defaults.d1_timeframe)
    parser.add_argument("--minimum-state-count", type=int, default=defaults.minimum_state_count)
    parser.add_argument("--minimum-transition-count", type=int, default=defaults.minimum_transition_count)
    parser.add_argument("--h4-window-size", type=int, default=defaults.h4_window_size)
    parser.add_argument("--d1-window-size", type=int, default=defaults.d1_window_size)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = TimestampedH4D1StateRegimeGenerationConfig(
        synchronized_data_dir=args.synchronized_data_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_state_count=args.minimum_state_count,
        minimum_transition_count=args.minimum_transition_count,
        h4_window_size=args.h4_window_size,
        d1_window_size=args.d1_window_size,
    )
    print(f"Synchronized data directory: {config.synchronized_data_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_timestamped_h4_d1_state_regime_generation(config)
    except Exception as exc:
        print(f"Timestamped H4/D1 state and regime generation failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("Timestamped H4/D1 state and regime generation completed")
    print(f"Source inventory rows: {len(result.source_inventory)}")
    print(f"H4 input rows: {len(result.h4_input_frame)}")
    print(f"D1 input rows: {len(result.d1_input_frame)}")
    print(f"H4 state rows: {len(result.h4_states)}")
    print(f"H4 transition rows: {len(result.h4_transitions)}")
    print(f"D1 state rows: {len(result.d1_states)}")
    if summary:
        print(f"Dominant generation coverage class: {summary.dominant_generation_coverage_class}")
        print(
            "Timestamped H4/D1 state regime readiness flag: "
            f"{summary.timestamped_h4_d1_state_regime_readiness_flag}"
        )
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {result.output_dir / 'timestamped_h4_d1_state_regime_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
