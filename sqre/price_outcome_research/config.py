"""Configuration for SQRE Price Outcome Research."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PriceOutcomeResearchConfig:
    forward_candles: list[int] = field(default_factory=lambda: [3, 6, 12])
    minimum_sample_size: int = 5
    pip_size: float = 0.0001
    strong_negative_threshold_pips: float = -20.0
    moderate_negative_threshold_pips: float = -5.0
    moderate_positive_threshold_pips: float = 5.0
    strong_positive_threshold_pips: float = 20.0
