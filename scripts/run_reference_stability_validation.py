#!/usr/bin/env python3
"""Run SQRE reference stability validation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.reference_stability_validation import (  # noqa: E402
    ReferenceStabilityValidationConfig,
    ReferenceStabilityValidationPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE reference stability validation")
    parser.add_argument("--reference-store-dir", type=Path, default=Path("data/research/research_reference_store_design"))
    parser.add_argument("--query-interface-dir", type=Path, default=Path("data/research/research_query_interface_design"))
    parser.add_argument("--snapshot-research-dir", type=Path, default=Path("data/research/current_market_state_snapshot_research"))
    parser.add_argument("--dashboard-dir", type=Path, default=Path("data/research/research_dashboard_prototype"))
    parser.add_argument("--manual-dashboard-review-dir", type=Path, default=Path("data/research/manual_research_dashboard_review"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/research/reference_stability_validation"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/research/reference_stability_validation/reference_stability_validation_report.txt"),
    )
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--minimum-stable-sample-size", type=int, default=20)
    parser.add_argument("--minimum-usable-sample-size", type=int, default=10)
    parser.add_argument("--maximum-stable-dispersion-pips", type=float, default=50.0)
    parser.add_argument("--maximum-usable-dispersion-pips", type=float, default=80.0)
    parser.add_argument("--minimum-query-coverage-ratio", type=float, default=0.60)
    parser.add_argument("--minimum-dashboard-card-count", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = ReferenceStabilityValidationConfig(
        reference_store_dir=args.reference_store_dir,
        query_interface_dir=args.query_interface_dir,
        snapshot_research_dir=args.snapshot_research_dir,
        dashboard_dir=args.dashboard_dir,
        manual_dashboard_review_dir=args.manual_dashboard_review_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_stable_sample_size=args.minimum_stable_sample_size,
        minimum_usable_sample_size=args.minimum_usable_sample_size,
        maximum_stable_dispersion_pips=args.maximum_stable_dispersion_pips,
        maximum_usable_dispersion_pips=args.maximum_usable_dispersion_pips,
        minimum_query_coverage_ratio=args.minimum_query_coverage_ratio,
        minimum_dashboard_card_count=args.minimum_dashboard_card_count,
    )
    print(f"Reference store: {config.reference_store_dir}")
    print(f"Query interface: {config.query_interface_dir}")
    print(f"Output directory: {config.output_dir}")
    result = ReferenceStabilityValidationPipeline(config).run()
    summary = result.summary
    print("Reference stability validation completed")
    if summary:
        print(f"Reference count: {summary.reference_count}")
        print(f"Core reference count: {summary.core_reference_count}")
        print(f"Supporting reference count: {summary.supporting_reference_count}")
        print(f"Query result count: {summary.query_result_count}")
        print(f"Dashboard reference card count: {summary.dashboard_reference_card_count}")
        print(f"Readiness class: {summary.dominant_reference_stability_readiness_class}")
        print(f"Readiness flag: {summary.reference_stability_readiness_flag}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
