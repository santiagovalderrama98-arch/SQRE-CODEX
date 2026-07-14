"""Configuration for master historical calibration summary building."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MasterCalibrationSummaryConfig:
    dedupe_key: str = "Scenario_ID"
    dedupe_policy: str = "last"
    allow_missing_inputs: bool = False

    def __post_init__(self) -> None:
        if self.dedupe_policy not in {"first", "last", "error"}:
            raise ValueError("dedupe_policy must be one of: first, last, error")
