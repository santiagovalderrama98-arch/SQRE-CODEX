#!/usr/bin/env python3
"""Run SQRE reference stability documentation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.reference_stability_documentation import (  # noqa: E402
    ReferenceStabilityDocumentationConfig,
    ReferenceStabilityDocumentationPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE reference stability documentation")
    parser.add_argument("--stability-validation-dir", type=Path, default=Path("data/research/reference_stability_validation"))
    parser.add_argument("--dashboard-dir", type=Path, default=Path("data/research/research_dashboard_prototype"))
    parser.add_argument("--manual-dashboard-review-dir", type=Path, default=Path("data/research/manual_research_dashboard_review"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/research/reference_stability_documentation"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/research/reference_stability_documentation/reference_stability_documentation_report.txt"),
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=Path("data/research/reference_stability_documentation/reference_stability_documentation.md"),
    )
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--documentation-title", default="SQRE Reference Stability Documentation")
    parser.add_argument("--include-dashboard-reading-guide", type=_bool_arg, default=True)
    parser.add_argument("--include-follow-up-plan", type=_bool_arg, default=True)
    parser.add_argument("--include-scope-safety-review", type=_bool_arg, default=True)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = ReferenceStabilityDocumentationConfig(
        stability_validation_dir=args.stability_validation_dir,
        dashboard_dir=args.dashboard_dir,
        manual_dashboard_review_dir=args.manual_dashboard_review_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        markdown_path=args.markdown,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        documentation_title=args.documentation_title,
        include_dashboard_reading_guide=args.include_dashboard_reading_guide,
        include_follow_up_plan=args.include_follow_up_plan,
        include_scope_safety_review=args.include_scope_safety_review,
    )
    print(f"Stability validation directory: {config.stability_validation_dir}")
    print(f"Dashboard directory: {config.dashboard_dir}")
    print(f"Manual dashboard review directory: {config.manual_dashboard_review_dir}")
    print(f"Output directory: {config.output_dir}")
    result = ReferenceStabilityDocumentationPipeline(config).run()
    print("Reference stability documentation completed")
    if result.summary:
        print(f"Stability dimensions: {result.summary.stability_dimension_count}")
        print(f"Dashboard guide elements: {result.summary.dashboard_guide_element_count}")
        print(f"Limitations documented: {result.summary.limitation_count}")
        print(f"Follow-up rows: {result.summary.follow_up_count}")
        print(f"Scope safety class: {result.summary.documentation_scope_safety_class}")
        print(f"Readiness class: {result.summary.reference_stability_documentation_readiness_class}")
        print(f"Readiness flag: {result.summary.reference_stability_documentation_readiness_flag}")
    print(f"Report path: {result.report_path}")
    print(f"Markdown path: {result.markdown_path}")
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
