#!/usr/bin/env python3
"""Run SQRE H4 timestamped context table generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_timestamped_context_table_generation import (  # noqa: E402
    H4TimestampedContextTableGenerationConfig,
    run_h4_timestamped_context_table_generation,
)


def parse_args() -> argparse.Namespace:
    defaults = H4TimestampedContextTableGenerationConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4 timestamped context table generation")
    parser.add_argument("--h4-combined-context-dir", type=Path, default=defaults.h4_combined_context_dir)
    parser.add_argument("--h4-d1-validation-dir", type=Path, default=defaults.h4_d1_validation_dir)
    parser.add_argument("--h4-d1-structural-research-dir", type=Path, default=defaults.h4_d1_structural_research_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--timeframe", default=defaults.timeframe)
    parser.add_argument("--minimum-scenario-coverage-ratio", type=float, default=defaults.minimum_scenario_coverage_ratio)
    parser.add_argument("--forward-windows", default=",".join(str(value) for value in defaults.forward_windows))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4TimestampedContextTableGenerationConfig(
        h4_combined_context_dir=args.h4_combined_context_dir,
        h4_d1_validation_dir=args.h4_d1_validation_dir,
        h4_d1_structural_research_dir=args.h4_d1_structural_research_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        timeframe=args.timeframe,
        minimum_scenario_coverage_ratio=args.minimum_scenario_coverage_ratio,
        forward_windows=_parse_windows(args.forward_windows),
    )
    print(f"H4 combined context directory: {config.h4_combined_context_dir}")
    print(f"H4/D1 validation directory: {config.h4_d1_validation_dir}")
    print(f"H4/D1 structural research directory: {config.h4_d1_structural_research_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_timestamped_context_table_generation(config)
    except Exception as exc:
        print(f"H4 timestamped context table generation failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4 timestamped context table generation completed")
    print(f"Source inventory rows: {len(result.source_inventory)}")
    print(f"Scenario inventory rows: {len(result.scenario_inventory)}")
    print(f"Timestamped context rows: {len(result.context_rows)}")
    print(f"Coverage review rows: {len(result.coverage_review)}")
    print(f"Missing context review rows: {len(result.missing_context_review)}")
    if summary:
        print(f"Dominant coverage class: {summary.dominant_coverage_class}")
        print(f"H4 timestamped context readiness flag: {summary.h4_timestamped_context_readiness_flag}")
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {result.output_dir / 'h4_timestamped_context_generation_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


def _parse_windows(raw: str) -> tuple[int, ...]:
    values: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(int(item))
    return tuple(values)


if __name__ == "__main__":
    sys.exit(main())
