"""Configuration for SQRE Transition Engine v1.0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransitionEngineConfig:
    confidence_change_threshold: float = 0.15
    structural_change_threshold: float = 0.10
    high_magnitude_threshold: float = 0.40
    low_magnitude_threshold: float = 0.20
    sequence_length: int = 3
