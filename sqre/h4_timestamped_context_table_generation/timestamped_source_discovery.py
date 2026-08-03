"""Recursive timestamped source discovery for H4 context generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqre.h4_timestamped_context_table_generation.loader import (
    SOURCE_STATE_ALIASES,
    TARGET_STATE_ALIASES,
    TIMESTAMP_ALIASES,
    read_optional_csv,
    resolve_column,
)


TIMESTAMPED_FILE_NAMES = [
    "state_transitions.csv",
    "market_states.csv",
    "states.csv",
    "transitions.csv",
    "h4_state_transitions.csv",
    "h4_market_states.csv",
    "scenario_state_transitions.csv",
    "scenario_market_states.csv",
    "forward_transition_outcomes.csv",
    "forward_state_outcomes.csv",
]


@dataclass(frozen=True)
class TimestampedSource:
    path: Path
    source_type: str
    timestamp_column: str
    rows_loaded: int


def discover_timestamped_sources(roots: list[Path]) -> list[TimestampedSource]:
    sources: list[TimestampedSource] = []
    expected_names = {name.lower() for name in TIMESTAMPED_FILE_NAMES}
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.csv")):
            if path.name.lower() not in expected_names:
                continue
            frame = read_optional_csv(path)
            timestamp_column = resolve_column(frame, TIMESTAMP_ALIASES)
            if frame.empty or timestamp_column is None:
                continue
            sources.append(
                TimestampedSource(
                    path=path,
                    source_type=_source_type(path, frame),
                    timestamp_column=timestamp_column,
                    rows_loaded=len(frame),
                )
            )
    return sources


def _source_type(path: Path, frame) -> str:
    name = path.name.lower()
    if "transition" in name or (
        resolve_column(frame, SOURCE_STATE_ALIASES) and resolve_column(frame, TARGET_STATE_ALIASES)
    ):
        return "TIMESTAMPED_TRANSITION_SOURCE"
    return "TIMESTAMPED_STATE_SOURCE"
