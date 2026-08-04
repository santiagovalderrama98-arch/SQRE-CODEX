#!/usr/bin/env python3
"""Run SQRE Research Query Interface Design."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.research_query_interface_design import (  # noqa: E402
    ResearchQueryInterfaceDesignConfig,
    ResearchQueryInterfaceDesignPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE Research Query Interface Design")
    parser.add_argument("--reference-store-dir", type=Path, required=True)
    parser.add_argument("--usage-review-dir", type=Path, required=True)
    parser.add_argument("--interpretation-dir", type=Path, default=Path("data/research/h4_d1_forward_outcome_interpretation_review"))
    parser.add_argument("--same-time-alignment-dir", type=Path, default=Path("data/research/h4_d1_same_time_alignment_table"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--preferred-horizons", default="1,2,3,6,12")
    parser.add_argument("--maximum-query-scenarios", type=int, default=500)
    parser.add_argument("--maximum-results-per-query", type=int, default=5)
    parser.add_argument("--minimum-reference-sample-size", type=int, default=10)
    parser.add_argument("--minimum-core-reference-sample-size", type=int, default=20)
    parser.add_argument("--maximum-reference-dispersion-pips", type=float, default=80.0)
    parser.add_argument("--query-h4-transition-label")
    parser.add_argument("--query-d1-market-state")
    parser.add_argument("--query-d1-regime-label")
    parser.add_argument("--query-d1-structure-direction")
    parser.add_argument("--query-forward-horizon", type=int)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = ResearchQueryInterfaceDesignConfig(
        reference_store_dir=args.reference_store_dir,
        usage_review_dir=args.usage_review_dir,
        interpretation_dir=args.interpretation_dir,
        same_time_alignment_dir=args.same_time_alignment_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        preferred_horizons=_parse_horizons(args.preferred_horizons),
        maximum_query_scenarios=args.maximum_query_scenarios,
        maximum_results_per_query=args.maximum_results_per_query,
        minimum_reference_sample_size=args.minimum_reference_sample_size,
        minimum_core_reference_sample_size=args.minimum_core_reference_sample_size,
        maximum_reference_dispersion_pips=args.maximum_reference_dispersion_pips,
        query_h4_transition_label=args.query_h4_transition_label,
        query_d1_market_state=args.query_d1_market_state,
        query_d1_regime_label=args.query_d1_regime_label,
        query_d1_structure_direction=args.query_d1_structure_direction,
        query_forward_horizon=args.query_forward_horizon,
    )
    print(f"Reference store directory: {config.reference_store_dir}")
    print(f"Usage review directory: {config.usage_review_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    result = ResearchQueryInterfaceDesignPipeline(config).run()
    summary = result.summary
    print("Research query interface design completed")
    if summary is not None:
        print(f"Research references: {summary.research_reference_count}")
        print(f"Query requests: {summary.research_query_request_count}")
        print(f"Query results: {summary.query_result_count}")
        print(f"Coverage ratio: {summary.research_query_coverage_ratio}")
        print(f"Readiness flag: {summary.research_query_interface_readiness_flag}")
    print(f"Results path: {config.output_dir / 'research_query_results.csv'}")
    print(f"Report path: {config.report_path}")
    return 0


def _parse_horizons(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())

