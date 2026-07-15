"""Configuration for D1 regime-normalized research."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class D1RegimeScenarioConfig:
    scenario_id: str
    timeframe: str
    regime_id: str
    regime_label: str


@dataclass(frozen=True)
class D1RegimeResearchConfig:
    research_name: str
    symbol: str
    timeframe: str
    scenarios: list[D1RegimeScenarioConfig]
    minimum_sample_size: int = 5
    high_regime_sensitivity_threshold: float = 0.35
    moderate_regime_sensitivity_threshold: float = 0.20
    forward_range_stability_threshold: float = 0.30
    minimum_regime_count: int = 2


def load_d1_regime_research_config(path: Path | str) -> D1RegimeResearchConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"D1 regime research config not found: {config_path}")

    import yaml

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    scenarios = [
        D1RegimeScenarioConfig(
            scenario_id=str(item["scenario_id"]),
            timeframe=str(item.get("timeframe", "D1")).upper(),
            regime_id=str(item["regime_id"]),
            regime_label=str(item["regime_label"]),
        )
        for item in raw.get("scenarios", [])
    ]
    invalid = [item.scenario_id for item in scenarios if item.timeframe != "D1"]
    if invalid:
        raise ValueError(f"D1 regime config contains non-D1 scenarios: {', '.join(invalid)}")
    if len({item.regime_id for item in scenarios}) != len(scenarios):
        raise ValueError("D1 regime config requires one unique regime per scenario")
    return D1RegimeResearchConfig(
        research_name=str(raw.get("research_name", "d1_regime_normalized_research")),
        symbol=str(raw.get("symbol", "EURUSD")),
        timeframe=str(raw.get("timeframe", "D1")).upper(),
        scenarios=scenarios,
        minimum_sample_size=int(raw.get("minimum_sample_size", 5)),
        high_regime_sensitivity_threshold=float(raw.get("high_regime_sensitivity_threshold", 0.35)),
        moderate_regime_sensitivity_threshold=float(raw.get("moderate_regime_sensitivity_threshold", 0.20)),
        forward_range_stability_threshold=float(raw.get("forward_range_stability_threshold", 0.30)),
        minimum_regime_count=int(raw.get("minimum_regime_count", 2)),
    )
