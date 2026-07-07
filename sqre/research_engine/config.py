"""Configuration for SQRE Research Engine v1.0."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResearchEngineConfig:
    forward_windows: list[int] = field(default_factory=lambda: [1, 2, 3])
    minimum_sample_size: int = 5
    sequence_length: int = 3
