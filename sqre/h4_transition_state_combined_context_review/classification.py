"""Shared classification helpers for H4 transition/state combined context review."""

from __future__ import annotations


def contains_any(value: str, markers: list[str]) -> bool:
    text = str(value or "").strip().upper()
    return any(marker in text for marker in markers)


def is_high(value: str) -> bool:
    return contains_any(value, ["HIGH", "SCENARIO_SENSITIVE"])


def is_sample_constrained(value: str) -> bool:
    return contains_any(value, ["SAMPLE", "CONSTRAINED"])


def is_unavailable(value: str) -> bool:
    text = str(value or "").strip().upper()
    return not text or contains_any(text, ["UNAVAILABLE", "MISSING", "INPUT_LIMITED"])


def is_moderate(value: str) -> bool:
    return contains_any(value, ["MODERATE"])


def is_stable(value: str) -> bool:
    return contains_any(value, ["STABLE", "DESCRIPTIVE", "CONSISTENT"])
