#!/usr/bin/env python3
"""Run SQRE dashboard stability indicators."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.dashboard_stability_indicators import (  # noqa: E402
    DashboardStabilityIndicatorsConfig,
    DashboardStabilityIndicatorsPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE dashboard stability indicators")
    parser.add_argument("--stability-documentation-dir", type=Path, default=Path("data/research/reference_stability_documentation"))
    parser.add_argument("--stability-validation-dir", type=Path, default=Path("data/research/reference_stability_validation"))
    parser.add_argument("--dashboard-dir", type=Path, default=Path("data/research/research_dashboard_prototype"))
    parser.add_argument("--manual-dashboard-review-dir", type=Path, default=Path("data/research/manual_research_dashboard_review"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/research/dashboard_stability_indicators"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/research/dashboard_stability_indicators/dashboard_stability_indicators_report.txt"),
    )
    parser.add_argument(
        "--html",
        type=Path,
        default=Path("data/research/dashboard_stability_indicators/dashboard_stability_indicators.html"),
    )
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--dashboard-title", default="SQRE Dashboard Stability Indicators")
    parser.add_argument("--maximum-reference-cards", type=int, default=10)
    parser.add_argument("--maximum-fallback-rows", type=int, default=15)
    parser.add_argument("--include-stability-legend", type=_bool_arg, default=True)
    parser.add_argument("--include-reference-card-indicators", type=_bool_arg, default=True)
    parser.add_argument("--include-dashboard-warnings", type=_bool_arg, default=True)
    parser.add_argument("--include-scope-safety-review", type=_bool_arg, default=True)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = DashboardStabilityIndicatorsConfig(
        stability_documentation_dir=args.stability_documentation_dir,
        stability_validation_dir=args.stability_validation_dir,
        dashboard_dir=args.dashboard_dir,
        manual_dashboard_review_dir=args.manual_dashboard_review_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        html_path=args.html,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        dashboard_title=args.dashboard_title,
        maximum_reference_cards=args.maximum_reference_cards,
        maximum_fallback_rows=args.maximum_fallback_rows,
        include_stability_legend=args.include_stability_legend,
        include_reference_card_indicators=args.include_reference_card_indicators,
        include_dashboard_warnings=args.include_dashboard_warnings,
        include_scope_safety_review=args.include_scope_safety_review,
    )
    print(f"Stability documentation directory: {config.stability_documentation_dir}")
    print(f"Stability validation directory: {config.stability_validation_dir}")
    print(f"Dashboard directory: {config.dashboard_dir}")
    print(f"Manual dashboard review directory: {config.manual_dashboard_review_dir}")
    print(f"Output directory: {config.output_dir}")
    result = DashboardStabilityIndicatorsPipeline(config).run()
    print("Dashboard stability indicators completed")
    if result.summary:
        print(f"Stability dimensions: {result.summary.stability_dimension_count}")
        print(f"Reference cards: {result.summary.reference_card_count}")
        print(f"Stable evidence indicators: {result.summary.stable_evidence_indicator_count}")
        print(f"Partial evidence indicators: {result.summary.partial_evidence_indicator_count}")
        print(f"Warning evidence indicators: {result.summary.warning_evidence_indicator_count}")
        print(f"Scope safety class: {result.summary.scope_safety_class}")
        print(f"Readiness class: {result.summary.dashboard_stability_readiness_class}")
        print(f"Readiness flag: {result.summary.dashboard_stability_readiness_flag}")
    print(f"Report path: {result.report_path}")
    print(f"HTML path: {result.html_path}")
    return 0


def _bool_arg(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


if __name__ == "__main__":
    raise SystemExit(main())
