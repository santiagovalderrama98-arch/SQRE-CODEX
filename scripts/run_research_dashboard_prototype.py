#!/usr/bin/env python3
"""Run the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.research_dashboard_prototype import (  # noqa: E402
    ResearchDashboardPrototypeConfig,
    ResearchDashboardPrototypePipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE Research Dashboard Prototype")
    parser.add_argument("--snapshot-research-dir", type=Path, required=True)
    parser.add_argument("--query-interface-dir", type=Path, default=Path("data/research/research_query_interface_design"))
    parser.add_argument("--reference-store-dir", type=Path, default=Path("data/research/research_reference_store_design"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--maximum-reference-cards", type=int, default=10)
    parser.add_argument("--maximum-fallback-rows", type=int, default=25)
    parser.add_argument("--dashboard-title", default="SQRE Research Dashboard Prototype")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = ResearchDashboardPrototypeConfig(
        snapshot_research_dir=args.snapshot_research_dir,
        query_interface_dir=args.query_interface_dir,
        reference_store_dir=args.reference_store_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        html_path=args.html,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        maximum_reference_cards=args.maximum_reference_cards,
        maximum_fallback_rows=args.maximum_fallback_rows,
        dashboard_title=args.dashboard_title,
    )
    print(f"Snapshot research directory: {config.snapshot_research_dir}")
    print(f"Query interface directory: {config.query_interface_dir}")
    print(f"Reference store directory: {config.reference_store_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    print(f"HTML: {config.html_path}")
    result = ResearchDashboardPrototypePipeline(config).run()
    summary = result.summary
    print("Research dashboard prototype completed")
    if summary is not None:
        print(f"Snapshot mode: {summary.snapshot_mode}")
        print(f"Snapshot source: {summary.snapshot_source}")
        print(f"Research references: {summary.research_reference_count}")
        print(f"Snapshot queries: {summary.snapshot_query_count}")
        print(f"Snapshot results: {summary.snapshot_result_count}")
        print(f"Coverage ratio: {summary.snapshot_reference_coverage_ratio}")
        print(f"Reference cards: {summary.reference_card_count}")
        print(f"Dashboard readiness class: {summary.dashboard_readiness_class}")
        print(f"Dashboard readiness flag: {summary.dashboard_readiness_flag}")
    print(f"Summary path: {config.output_dir / 'research_dashboard_summary.csv'}")
    print(f"Report path: {config.report_path}")
    print(f"HTML path: {config.html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
