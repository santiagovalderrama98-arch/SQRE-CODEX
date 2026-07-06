#!/usr/bin/env python3
"""Run SQRE Phase 6 Transition Engine."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.transition_engine import TransitionEngineConfig, run_transition_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE transition engine")
    parser.add_argument("--states", required=True, help="Input market states CSV path")
    parser.add_argument("--output-dir", required=True, help="Output directory for transition CSV files")
    parser.add_argument("--report", required=True, help="Output transition engine report path")
    parser.add_argument("--confidence-change-threshold", type=float, default=0.15)
    parser.add_argument("--structural-change-threshold", type=float, default=0.10)
    parser.add_argument("--high-magnitude-threshold", type=float, default=0.40)
    parser.add_argument("--low-magnitude-threshold", type=float, default=0.20)
    parser.add_argument("--sequence-length", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = TransitionEngineConfig(
        confidence_change_threshold=args.confidence_change_threshold,
        structural_change_threshold=args.structural_change_threshold,
        high_magnitude_threshold=args.high_magnitude_threshold,
        low_magnitude_threshold=args.low_magnitude_threshold,
        sequence_length=args.sequence_length,
    )

    try:
        summary = run_transition_engine(
            states_path=args.states,
            output_dir=args.output_dir,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("Transition engine failed")
        print(f"Transition engine failed: {exc}")
        return 1

    matrix_rows = _count_csv_rows(summary.transition_matrix_path)
    sequence_rows = _count_csv_rows(summary.transition_sequences_path)
    print("Transition engine completed")
    print(f"States processed: {summary.states_processed}")
    print(f"Transitions generated: {summary.transitions_generated}")
    print(f"Transition matrix rows: {matrix_rows}")
    print(f"Transition sequences: {sequence_rows}")
    print(f"State transitions path: {summary.state_transitions_path}")
    print(f"Transition matrix path: {summary.transition_matrix_path}")
    print(f"Transition sequences path: {summary.transition_sequences_path}")
    print(f"Report path: {summary.report_path}")
    return 0


def _count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


if __name__ == "__main__":
    raise SystemExit(main())
