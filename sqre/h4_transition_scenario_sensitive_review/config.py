"""Configuration for H4 transition scenario-sensitive profile review."""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_FOCUS_TRANSITIONS = (
    "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT",
    "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION",
    "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT",
    "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT",
)


@dataclass(frozen=True)
class H4TransitionScenarioSensitiveReviewConfig:
    moderate_deviation_threshold: float = 0.20
    high_deviation_threshold: float = 0.35
    near_candidate_high_deviation_max: int = 1
    minimum_total_sample_size: int = 20
    minimum_scenario_count: int = 2
    focus_transitions: tuple[str, ...] = DEFAULT_FOCUS_TRANSITIONS
