"""Config loading and run generation for state threshold experiments."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqre.state_threshold_experiments.models import (
    BaseStateThresholdScenario,
    StateThresholdExperimentConfig,
    StateThresholdExperimentRun,
)


def load_state_threshold_experiment_config(path: Path | str) -> StateThresholdExperimentConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"State threshold experiment config not found: {config_path}")
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to load state threshold experiment YAML configs.") from exc
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("State threshold experiment config must be a YAML mapping.")
    return _parse_config(raw)


def build_experiment_runs(
    config: StateThresholdExperimentConfig,
    output_dir: Path | str,
    profile_filter: str | None = None,
    scenario_filter: str | None = None,
) -> list[StateThresholdExperimentRun]:
    output_root = Path(output_dir)
    runs: list[StateThresholdExperimentRun] = []
    for scenario in config.base_scenarios:
        if scenario_filter and scenario.scenario_id != scenario_filter:
            continue
        duration = config.baseline_max_structure_duration_seconds.get(scenario.timeframe)
        if duration is None:
            continue
        for profile_id in config.profiles:
            if profile_filter and profile_id != profile_filter:
                continue
            output = output_root / profile_id / scenario.scenario_id
            runs.append(
                StateThresholdExperimentRun(
                    experiment_run_id=f"{profile_id}__{scenario.scenario_id}",
                    profile_id=profile_id,
                    scenario_id=scenario.scenario_id,
                    symbol=scenario.symbol,
                    timeframe=scenario.timeframe,
                    ohlc_path=scenario.ohlc_path,
                    state_config_path=config.state_config_path,
                    max_structure_duration_seconds=duration,
                    minimum_sample_size=config.minimum_sample_size,
                    forward_candles=list(config.forward_candles),
                    output_dir=output,
                    processed_dir=output / "processed",
                    research_dir=output / "research",
                    reports_dir=output / "reports",
                )
            )
    return runs


def _parse_config(raw: dict[str, Any]) -> StateThresholdExperimentConfig:
    _require(
        raw,
        [
            "experiment_name",
            "symbol",
            "pip_size",
            "forward_candles",
            "minimum_sample_size",
            "baseline_max_structure_duration_seconds",
            "state_config_path",
            "base_scenarios",
            "profiles",
        ],
    )
    return StateThresholdExperimentConfig(
        experiment_name=str(raw["experiment_name"]),
        symbol=str(raw["symbol"]),
        pip_size=float(raw["pip_size"]),
        forward_candles=[int(item) for item in _list(raw["forward_candles"], "forward_candles")],
        minimum_sample_size=int(raw["minimum_sample_size"]),
        baseline_max_structure_duration_seconds={
            str(key): int(value)
            for key, value in _mapping(
                raw["baseline_max_structure_duration_seconds"],
                "baseline_max_structure_duration_seconds",
            ).items()
        },
        state_config_path=Path(str(raw["state_config_path"])),
        base_scenarios=[_parse_scenario(item) for item in _list(raw["base_scenarios"], "base_scenarios")],
        profiles=[str(item) for item in _list(raw["profiles"], "profiles")],
    )


def _parse_scenario(raw: Any) -> BaseStateThresholdScenario:
    item = _mapping(raw, "base_scenarios item")
    _require(item, ["scenario_id", "symbol", "timeframe", "ohlc_path"])
    return BaseStateThresholdScenario(
        scenario_id=str(item["scenario_id"]),
        symbol=str(item["symbol"]),
        timeframe=str(item["timeframe"]),
        ohlc_path=Path(str(item["ohlc_path"])),
    )


def _require(mapping: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if field not in mapping]
    if missing:
        raise ValueError(f"Missing required state threshold experiment config field(s): {', '.join(missing)}")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping.")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list.")
    return value
