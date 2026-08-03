#!/usr/bin/env python3
"""Run SQRE H4/D1 synchronized historical data preparation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_synchronized_data_preparation import (  # noqa: E402
    H4D1SynchronizedDataPreparationConfig,
    run_h4_d1_synchronized_data_preparation,
)


def parse_args() -> argparse.Namespace:
    defaults = H4D1SynchronizedDataPreparationConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 synchronized historical data preparation")
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--h4-input", type=Path, default=defaults.h4_input)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--start-date", default=defaults.start_date)
    parser.add_argument("--end-date", default=defaults.end_date)
    parser.add_argument("--timezone", default=defaults.timezone)
    parser.add_argument("--minimum-h4-continuity-ratio", type=float, default=defaults.minimum_h4_continuity_ratio)
    parser.add_argument("--minimum-d1-h4-candle-count", type=int, default=defaults.minimum_d1_h4_candle_count)
    parser.add_argument("--expected-h4-candles-per-d1", type=int, default=defaults.expected_h4_candles_per_d1)
    parser.add_argument("--build-d1-from-h4", default=str(defaults.build_d1_from_h4).lower())
    parser.add_argument("--allow-download", default=str(defaults.allow_download).lower())
    parser.add_argument("--provider", default=defaults.provider)
    parser.add_argument("--validation-config", type=Path, default=defaults.validation_config)
    parser.add_argument("--validation-summary", type=Path, default=defaults.validation_summary)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4D1SynchronizedDataPreparationConfig(
        symbol=args.symbol,
        h4_input=args.h4_input,
        output_dir=args.output_dir,
        report_path=args.report,
        start_date=args.start_date,
        end_date=args.end_date,
        timezone=args.timezone,
        minimum_h4_continuity_ratio=args.minimum_h4_continuity_ratio,
        minimum_d1_h4_candle_count=args.minimum_d1_h4_candle_count,
        expected_h4_candles_per_d1=args.expected_h4_candles_per_d1,
        build_d1_from_h4=_parse_bool(args.build_d1_from_h4),
        allow_download=_parse_bool(args.allow_download),
        provider=args.provider,
        validation_config=args.validation_config,
        validation_summary=args.validation_summary,
    )
    print(f"Symbol: {config.symbol}")
    print(f"H4 input: {config.h4_input}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_d1_synchronized_data_preparation(config)
    except Exception as exc:
        print(f"H4/D1 synchronized data preparation failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4/D1 synchronized data preparation completed")
    print(f"Source inventory rows: {len(result.source_inventory)}")
    print(f"H4 row count: {len(result.h4_frame)}")
    print(f"D1 row count: {len(result.d1_frame)}")
    print(f"Aligned H4 row count: {summary.aligned_h4_row_count if summary else 0}")
    print(f"Unaligned H4 row count: {summary.unaligned_h4_row_count if summary else 0}")
    if summary:
        print(f"Continuity ratio: {summary.continuity_ratio}")
        print(f"Synchronization coverage ratio: {summary.synchronization_coverage_ratio}")
        print(f"Dominant synchronization quality class: {summary.dominant_synchronization_quality_class}")
        print(f"H4/D1 synchronized data readiness flag: {summary.h4_d1_synchronized_data_readiness_flag}")
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {result.output_dir / 'h4_d1_synchronized_data_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


if __name__ == "__main__":
    sys.exit(main())
