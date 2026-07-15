"""Scenario-period regime mapping."""

from __future__ import annotations

from sqre.d1_regime_normalized_research.config import D1RegimeResearchConfig, D1RegimeScenarioConfig


def build_regime_lookup(config: D1RegimeResearchConfig) -> dict[str, D1RegimeScenarioConfig]:
    return {scenario.scenario_id: scenario for scenario in config.scenarios}


def map_scenario_to_regime(config: D1RegimeResearchConfig, scenario_id: str) -> D1RegimeScenarioConfig:
    lookup = build_regime_lookup(config)
    if scenario_id not in lookup:
        raise KeyError(f"Scenario is not configured for D1 regime research: {scenario_id}")
    return lookup[scenario_id]
