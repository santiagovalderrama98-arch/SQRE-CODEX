#!/usr/bin/env python3
"""Run SQRE manual research dashboard review."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.manual_research_dashboard_review import (  # noqa: E402
    ManualResearchDashboardReviewConfig,
    ManualResearchDashboardReviewPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE manual research dashboard review")
    parser.add_argument("--dashboard-dir", type=Path, required=True)
    parser.add_argument("--snapshot-research-dir", type=Path, default=Path("data/research/current_market_state_snapshot_research"))
    parser.add_argument("--query-interface-dir", type=Path, default=Path("data/research/research_query_interface_design"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--maximum-reference-cards", type=int, default=10)
    parser.add_argument("--maximum-fallback-rows", type=int, default=15)
    parser.add_argument("--dashboard-title", default="SQRE Manual Research Dashboard Review")
    parser.add_argument("--include-field-usefulness-review", type=_bool, default=True)
    parser.add_argument("--include-redundancy-review", type=_bool, default=True)
    parser.add_argument("--include-scope-safety-review", type=_bool, default=True)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = ManualResearchDashboardReviewConfig(
        dashboard_dir=args.dashboard_dir,
        snapshot_research_dir=args.snapshot_research_dir,
        query_interface_dir=args.query_interface_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        html_path=args.html,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        maximum_reference_cards=args.maximum_reference_cards,
        maximum_fallback_rows=args.maximum_fallback_rows,
        dashboard_title=args.dashboard_title,
        include_field_usefulness_review=args.include_field_usefulness_review,
        include_redundancy_review=args.include_redundancy_review,
        include_scope_safety_review=args.include_scope_safety_review,
    )
    print(f"Dashboard directory: {config.dashboard_dir}")
    print(f"Snapshot research directory: {config.snapshot_research_dir}")
    print(f"Query interface directory: {config.query_interface_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    print(f"HTML: {config.html_path}")
    result = ManualResearchDashboardReviewPipeline(config).run()
    print("Manual research dashboard review completed")
    if result.summary is not None:
        summary = result.summary
        print(f"Panel completeness ready count: {summary.panel_completeness_ready_count}")
        print(f"Panel completeness partial count: {summary.panel_completeness_partial_count}")
        print(f"Panel completeness missing count: {summary.panel_completeness_missing_count}")
        print(f"High readability panel count: {summary.high_readability_panel_count}")
        print(f"Moderate readability panel count: {summary.moderate_readability_panel_count}")
        print(f"Low readability panel count: {summary.low_readability_panel_count}")
        print(f"Scope safety class: {summary.scope_safety_class}")
        print(f"Scope violation count: {summary.scope_violation_count}")
        print(f"Recommendation count: {summary.recommendation_count}")
        print(f"Dashboard usability readiness class: {summary.dashboard_usability_readiness_class}")
        print(f"Dashboard usability readiness flag: {summary.dashboard_usability_readiness_flag}")
    print(f"Summary path: {config.output_dir / 'manual_research_dashboard_review_summary.csv'}")
    print(f"Report path: {config.report_path}")
    print(f"HTML path: {config.html_path}")
    return 0


def _bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y"}


if __name__ == "__main__":
    raise SystemExit(main())
