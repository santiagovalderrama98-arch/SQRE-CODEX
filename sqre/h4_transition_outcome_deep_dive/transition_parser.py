"""Transition label parsing for H4 transition outcome deep dive."""

from __future__ import annotations

import re

from sqre.h4_transition_outcome_deep_dive.models import TransitionParseResult


KNOWN_STATES = [
    "DIRECTIONAL_DISPLACEMENT",
    "DIRECTIONAL_EXPANSION",
    "DIRECTIONAL_DRIFT",
    "VOLATILE_ROTATION",
    "LOW_QUALITY_STRUCTURE",
    "NEUTRAL_COMPRESSION",
    "COMPLEX_CONSOLIDATION",
    "UNCLASSIFIED",
]


def parse_transition_label(label: str) -> TransitionParseResult:
    normalized = _normalize_label(label)
    states = _states_in_order(normalized)
    if len(states) < 2:
        return TransitionParseResult("UNKNOWN", "UNKNOWN", "UNKNOWN_TRANSITION_FAMILY")
    source, target = states[0], states[1]
    return TransitionParseResult(source, target, _transition_family(source, target))


def _normalize_label(label: str) -> str:
    text = str(label).upper().strip()
    text = text.replace("TRANSITION:", "")
    text = text.replace("->", " ")
    text = text.replace("_TO_", " ")
    text = text.replace("|", " ")
    text = text.replace("__", " ")
    text = text.replace("/", " ")
    text = text.replace(":", " ")
    return re.sub(r"\s+", " ", text)


def _states_in_order(label: str) -> list[str]:
    matches: list[tuple[int, str]] = []
    for state in KNOWN_STATES:
        for match in re.finditer(re.escape(state), label):
            matches.append((match.start(), state))
    return [state for _, state in sorted(matches)]


def _transition_family(source: str, target: str) -> str:
    if source == "UNKNOWN" or target == "UNKNOWN":
        return "UNKNOWN_TRANSITION_FAMILY"
    source_directional = source.startswith("DIRECTIONAL")
    target_directional = target.startswith("DIRECTIONAL")
    if source_directional and target_directional:
        return "DIRECTIONAL_TO_DIRECTIONAL"
    if source_directional and target == "VOLATILE_ROTATION":
        return "DIRECTIONAL_TO_ROTATION"
    if source == "VOLATILE_ROTATION" and target_directional:
        return "ROTATION_TO_DIRECTIONAL"
    if source == "LOW_QUALITY_STRUCTURE" or target == "LOW_QUALITY_STRUCTURE":
        return "QUALITY_TO_OTHER"
    return "OTHER_TRANSITION_FAMILY"
