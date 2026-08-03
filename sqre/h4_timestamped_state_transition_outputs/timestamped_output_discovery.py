"""Recursive timestamped state/transition output discovery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.loader import (
    SOURCE_STATE_ALIASES,
    TARGET_STATE_ALIASES,
    TIMESTAMP_ALIASES,
    read_optional_csv,
    resolve_column,
)


TIMESTAMPED_FILE_NAMES = [
    "market_states.csv",
    "states.csv",
    "h4_market_states.csv",
    "scenario_market_states.csv",
    "state_transitions.csv",
    "transitions.csv",
    "h4_state_transitions.csv",
    "scenario_state_transitions.csv",
]


@dataclass(frozen=True)
class TimestampedOutputSource:
    path: Path
    source_type: str
    timestamp_column: str
    rows_loaded: int


def discover_timestamped_outputs(roots: list[Path]) -> list[TimestampedOutputSource]:
    sources: list[TimestampedOutputSource] = []
    names = {name.lower() for name in TIMESTAMPED_FILE_NAMES}
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.csv")):
            if path.name.lower() not in names or path in seen:
                continue
            seen.add(path)
            frame = read_optional_csv(path)
            timestamp_column = resolve_column(frame, TIMESTAMP_ALIASES)
            if frame.empty or timestamp_column is None:
                continue
            sources.append(
                TimestampedOutputSource(
                    path=path,
                    source_type=_source_type(path, frame),
                    timestamp_column=timestamp_column,
                    rows_loaded=len(frame),
                )
            )
    return sources


def _source_type(path: Path, frame) -> str:
    name = path.name.lower()
    if "transition" in name:
        return "TIMESTAMPED_TRANSITION_SOURCE"
    if resolve_column(frame, SOURCE_STATE_ALIASES) and resolve_column(frame, TARGET_STATE_ALIASES):
        return "TIMESTAMPED_TRANSITION_SOURCE"
    return "TIMESTAMPED_STATE_SOURCE"
