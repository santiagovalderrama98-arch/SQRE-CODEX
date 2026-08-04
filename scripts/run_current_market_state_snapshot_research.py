#!/usr/bin/env python3
"""Run SQRE Current Market State Snapshot Research."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.current_market_state_snapshot_research import (  # noqa: E402
    CurrentMarketStateSnapshotResearchConfig,
    CurrentMarketStateSnapshotResearchPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE Current Market State Snapshot Research")
    parser.add_argument("--reference-store-dir", type=Path, required=True)
    parser.add_argument("--query-interface-dir", type=Path, required=True)
    parser.add_argument("--usage-review-dir", type=Path, default=Path("data/research/research_reference_store_usage_review"))
    parser.add_argument("--same-time-alignment-dir", type=Path, default=Path("data/research/h4_d1_same_time_alignment_table"))
    parser.add_argument(
        "--timestamped-state-regime-dir", type=Path, default=Path("data/research/h4_d1_timestamped_state_regime_table")
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--snapshot-mode", default="LATEST_AVAILABLE_SNAPSHOT")
    parser.add_argument("--snapshot-timestamp")
    parser.add_argument("--snapshot-h4-transition-label")
    parser.add_argument("--snapshot-h4-market-state")
    parser.add_argument("--snapshot-d1-market-state")
    parser.add_argument("--snapshot-d1-regime-label")
    parser.add_argument("--snapshot-d1-structure-direction")
    parser.add_argument("--snapshot-forward-horizon", type=int)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--preferred-horizons", default="1,2,3,6,12")
    parser.add_argument("--maximum-results-per-snapshot-query", type=int, default=5)
    parser.add_argument("--minimum-reference-sample-size", type=int, default=10)
    parser.add_argument("--minimum-core-reference-sample-size", type=int, default=20)
    parser.add_argument("--maximum-reference-dispersion-pips", type=float, default=80.0)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = CurrentMarketStateSnapshotResearchConfig(
        reference_store_dir=args.reference_store_dir,
        query_interface_dir=args.query_interface_dir,
        usage_review_dir=args.usage_review_dir,
        same_time_alignment_dir=args.same_time_alignment_dir,
        timestamped_state_regime_dir=args.timestamped_state_regime_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        snapshot_mode=args.snapshot_mode,
        snapshot_timestamp=args.snapshot_timestamp,
        snapshot_h4_transition_label=args.snapshot_h4_transition_label,
        snapshot_h4_market_state=args.snapshot_h4_market_state,
        snapshot_d1_market_state=args.snapshot_d1_market_state,
        snapshot_d1_regime_label=args.snapshot_d1_regime_label,
        snapshot_d1_structure_direction=args.snapshot_d1_structure_direction,
        snapshot_forward_horizon=args.snapshot_forward_horizon,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        preferred_horizons=_parse_horizons(args.preferred_horizons),
        maximum_results_per_snapshot_query=args.maximum_results_per_snapshot_query,
        minimum_reference_sample_size=args.minimum_reference_sample_size,
        minimum_core_reference_sample_size=args.minimum_core_reference_sample_size,
        maximum_reference_dispersion_pips=args.maximum_reference_dispersion_pips,
    )
    print(f"Reference store directory: {config.reference_store_dir}")
    print(f"Query interface directory: {config.query_interface_dir}")
    print(f"Snapshot mode: {config.normalized_snapshot_mode()}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    result = CurrentMarketStateSnapshotResearchPipeline(config).run()
    summary = result.summary
    print("Current market state snapshot research completed")
    if summary is not None:
        print(f"Snapshot source: {summary.snapshot_source}")
        print(f"Snapshot validation: {summary.snapshot_validation_status}")
        print(f"Research references: {summary.research_reference_count}")
        print(f"Snapshot queries: {summary.snapshot_query_count}")
        print(f"Snapshot results: {summary.snapshot_result_count}")
        print(f"Coverage ratio: {summary.snapshot_reference_coverage_ratio}")
        print(f"Readiness flag: {summary.current_market_state_snapshot_readiness_flag}")
    print(f"Results path: {config.output_dir / 'current_market_state_snapshot_reference_results.csv'}")
    print(f"Report path: {config.report_path}")
    return 0


def _parse_horizons(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
