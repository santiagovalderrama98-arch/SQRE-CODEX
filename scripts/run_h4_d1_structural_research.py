#!/usr/bin/env python3
"""Run SQRE H4/D1 structural research."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_structural_research import H4D1StructuralResearchConfig, run_h4_d1_structural_research


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 structural research")
    parser.add_argument("--validation-summary", required=True, type=Path)
    parser.add_argument("--validation-output-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--minimum-sample-size", type=int, default=5)
    parser.add_argument("--high-low-sample-rate", type=float, default=0.50)
    parser.add_argument("--high-scenario-cv-threshold", type=float, default=0.35)
    parser.add_argument("--high-regime-sensitivity-threshold", type=float, default=0.35)
    parser.add_argument("--forward-range-stability-threshold", type=float, default=0.30)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    config = H4D1StructuralResearchConfig(
        minimum_sample_size=args.minimum_sample_size,
        high_low_sample_rate=args.high_low_sample_rate,
        high_scenario_cv_threshold=args.high_scenario_cv_threshold,
        high_regime_sensitivity_threshold=args.high_regime_sensitivity_threshold,
        forward_range_stability_threshold=args.forward_range_stability_threshold,
    )

    print("SQRE H4/D1 structural research started")
    print(f"Validation summary: {args.validation_summary}")
    print(f"Validation output directory: {args.validation_output_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_h4_d1_structural_research(
            validation_summary=args.validation_summary,
            validation_output_dir=args.validation_output_dir,
            output_dir=args.output_dir,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("H4/D1 structural research failed")
        print(f"H4/D1 structural research failed: {exc}")
        return 1

    h4_count = sum(1 for row in result.inventory_rows if row.timeframe == "H4")
    d1_count = sum(1 for row in result.inventory_rows if row.timeframe == "D1")
    print("H4/D1 structural research completed")
    print(f"Scenarios loaded: {result.scenarios_loaded}")
    print(f"H4 scenarios processed: {h4_count}")
    print(f"D1 scenarios processed: {d1_count}")
    print(f"State profiles: {len(result.state_profiles)}")
    print(f"Transition profiles: {len(result.transition_profiles)}")
    print(f"Price outcome profiles: {len(result.price_outcome_profiles)}")
    print(f"Sequence profiles: {len(result.sequence_profiles)}")
    print(f"Scenario inventory path: {args.output_dir / 'h4_d1_scenario_inventory.csv'}")
    print(f"Timeframe summary path: {args.output_dir / 'h4_d1_timeframe_research_summary.csv'}")
    print(f"Report path: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
