#!/usr/bin/env python3
"""Run SQRE Phase 4 Market Structure."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.market_structure import MarketStructureConfig, MarketStructurePipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE market structure analysis")
    parser.add_argument("--events", required=True, help="Input events CSV path")
    parser.add_argument("--output-dir", required=True, help="Output directory for structural CSVs")
    parser.add_argument("--report", required=True, help="Output market structure report path")
    parser.add_argument("--min-leg-pips", type=float, default=3.0)
    parser.add_argument("--pip-size", type=float, default=0.0001)
    parser.add_argument("--min-structure-confidence", type=float, default=0.40)
    parser.add_argument("--max-structure-duration-seconds", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    print(f"Input events: {args.events}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")

    config = MarketStructureConfig(
        pip_size=args.pip_size,
        min_leg_pips=args.min_leg_pips,
        min_structure_confidence=args.min_structure_confidence,
        max_structure_duration_seconds=args.max_structure_duration_seconds,
    )
    pipeline = MarketStructurePipeline(config=config)

    try:
        result = pipeline.run(
            events_path=args.events,
            output_dir=args.output_dir,
            report_path=args.report,
        )
    except Exception as exc:
        logging.exception("Market structure failed")
        print(f"Market structure failed: {exc}")
        return 1

    print(result.message)
    print(f"Events processed: {result.events_processed}")
    print(f"Structural points: {result.structural_points}")
    print(f"Legs created: {result.legs_created}")
    print(f"Structures detected: {result.structures_detected}")
    print(f"Structures path: {result.structures_path}")
    print(f"Structure events path: {result.structure_events_path}")
    print(f"Structural units path: {result.structural_units_path}")
    print(f"Structural fingerprints path: {result.structural_fingerprints_path}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
