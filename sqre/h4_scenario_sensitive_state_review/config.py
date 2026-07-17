"""Configuration for H4 scenario-sensitive state profile review."""

from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_FOCUS_STATES = ("DIRECTIONAL_DISPLACEMENT", "DIRECTIONAL_EXPANSION", "VOLATILE_ROTATION")


@dataclass(frozen=True)
class H4ScenarioSensitiveStateReviewConfig:
    moderate_deviation_threshold: float = 0.20
    high_deviation_threshold: float = 0.35
    near_candidate_high_deviation_max: int = 1
    minimum_total_sample_size: int = 20
    minimum_scenario_count: int = 2
    focus_states: tuple[str, ...] = field(default_factory=lambda: DEFAULT_FOCUS_STATES)

    @classmethod
    def from_focus_states_text(cls, text: str | None) -> "H4ScenarioSensitiveStateReviewConfig":
        if not text:
            return cls()
        states = tuple(item.strip().upper() for item in text.split(",") if item.strip())
        return cls(focus_states=states or DEFAULT_FOCUS_STATES)
