"""Configuration loading and run generation for calibration experiments."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqre.calibration_experiments.models import (
    BaseExperimentScenario,
    CalibrationExperimentConfig,
    DurationExperiment,
    ExperimentRun,
    SampleSizeExperiment,
)


BASELINE_DURATION_SECONDS = {
    "H4": 604800,
    "D1": 2592000,
}
BASELINE_MINIMUM_SAMPLE_SIZE = 5


def load_calibration_experiment_config(path: Path | str) -> CalibrationExperimentConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Calibration experiment config not found: {config_path}")
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to load calibration experiment YAML configs.") from exc
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Calibration experiment config must be a YAML mapping.")
    return _parse_config(raw)


def build_experiment_runs(
    config: CalibrationExperimentConfig,
    output_dir: Path | str,
    experiment_filter: str | None = None,
    experiment_type_filter: str | None = None,
    scenario_filter: str | None = None,
) -> list[ExperimentRun]:
    output_root = Path(output_dir)
    runs: list[ExperimentRun] = []
    for scenario in config.base_scenarios:
        if scenario_filter and scenario.scenario_id != scenario_filter:
            continue
        runs.extend(_duration_runs(config, scenario, output_root))
        runs.extend(_sample_size_runs(config, scenario, output_root))
    return [
        run
        for run in runs
        if _matches_filters(run, experiment_filter, experiment_type_filter)
    ]


def _parse_config(raw: dict[str, Any]) -> CalibrationExperimentConfig:
    _require(raw, ["experiment_name", "symbol", "pip_size", "forward_candles", "base_scenarios"])
    _require(raw, ["duration_experiments", "sample_size_experiments"])
    forward_candles = _int_list(raw["forward_candles"], "forward_candles")
    if not forward_candles:
        raise ValueError("forward_candles must include at least one value.")
    return CalibrationExperimentConfig(
        experiment_name=str(raw["experiment_name"]),
        symbol=str(raw["symbol"]),
        pip_size=float(raw["pip_size"]),
        forward_candles=forward_candles,
        base_scenarios=[_parse_scenario(item) for item in _list(raw["base_scenarios"], "base_scenarios")],
        duration_experiments=[
            _parse_duration(item) for item in _list(raw["duration_experiments"], "duration_experiments")
        ],
        sample_size_experiments=[
            _parse_sample_size(item) for item in _list(raw["sample_size_experiments"], "sample_size_experiments")
        ],
    )


def _parse_scenario(raw: Any) -> BaseExperimentScenario:
    item = _mapping(raw, "base_scenarios item")
    _require(item, ["scenario_id", "symbol", "timeframe", "ohlc_path"])
    return BaseExperimentScenario(
        scenario_id=str(item["scenario_id"]),
        symbol=str(item["symbol"]),
        timeframe=str(item["timeframe"]),
        ohlc_path=Path(str(item["ohlc_path"])),
    )


def _parse_duration(raw: Any) -> DurationExperiment:
    item = _mapping(raw, "duration_experiments item")
    _require(item, ["experiment_id", "max_structure_duration_seconds"])
    durations = _mapping(item["max_structure_duration_seconds"], "max_structure_duration_seconds")
    return DurationExperiment(
        experiment_id=str(item["experiment_id"]),
        description=str(item.get("description", "")),
        max_structure_duration_seconds_by_timeframe={
            str(timeframe): int(seconds) for timeframe, seconds in durations.items()
        },
    )


def _parse_sample_size(raw: Any) -> SampleSizeExperiment:
    item = _mapping(raw, "sample_size_experiments item")
    _require(item, ["experiment_id", "minimum_sample_size"])
    return SampleSizeExperiment(
        experiment_id=str(item["experiment_id"]),
        description=str(item.get("description", "")),
        minimum_sample_size=int(item["minimum_sample_size"]),
    )


def _duration_runs(
    config: CalibrationExperimentConfig,
    scenario: BaseExperimentScenario,
    output_root: Path,
) -> list[ExperimentRun]:
    runs = []
    for experiment in config.duration_experiments:
        duration = experiment.max_structure_duration_seconds_by_timeframe.get(scenario.timeframe)
        if duration is None:
            continue
        runs.append(
            _run(
                experiment_type="DURATION",
                experiment_id=experiment.experiment_id,
                scenario=scenario,
                output_root=output_root,
                max_structure_duration_seconds=duration,
                minimum_sample_size=BASELINE_MINIMUM_SAMPLE_SIZE,
                forward_candles=config.forward_candles,
            )
        )
    return runs


def _sample_size_runs(
    config: CalibrationExperimentConfig,
    scenario: BaseExperimentScenario,
    output_root: Path,
) -> list[ExperimentRun]:
    duration = BASELINE_DURATION_SECONDS.get(scenario.timeframe)
    if duration is None:
        return []
    return [
        _run(
            experiment_type="SAMPLE_SIZE",
            experiment_id=experiment.experiment_id,
            scenario=scenario,
            output_root=output_root,
            max_structure_duration_seconds=duration,
            minimum_sample_size=experiment.minimum_sample_size,
            forward_candles=config.forward_candles,
        )
        for experiment in config.sample_size_experiments
    ]


def _run(
    *,
    experiment_type: str,
    experiment_id: str,
    scenario: BaseExperimentScenario,
    output_root: Path,
    max_structure_duration_seconds: int,
    minimum_sample_size: int,
    forward_candles: list[int],
) -> ExperimentRun:
    experiment_run_id = f"{experiment_id}__{scenario.scenario_id}"
    output_dir = output_root / experiment_id / scenario.scenario_id
    processed_dir = output_dir / "processed"
    research_dir = output_dir / "research"
    reports_dir = output_dir / "reports"
    return ExperimentRun(
        experiment_run_id=experiment_run_id,
        experiment_type=experiment_type,
        experiment_id=experiment_id,
        scenario_id=scenario.scenario_id,
        symbol=scenario.symbol,
        timeframe=scenario.timeframe,
        ohlc_path=scenario.ohlc_path,
        max_structure_duration_seconds=max_structure_duration_seconds,
        minimum_sample_size=minimum_sample_size,
        forward_candles=list(forward_candles),
        output_dir=output_dir,
        processed_dir=processed_dir,
        research_dir=research_dir,
        reports_dir=reports_dir,
    )


def _matches_filters(
    run: ExperimentRun,
    experiment_filter: str | None,
    experiment_type_filter: str | None,
) -> bool:
    if experiment_filter and run.experiment_id != experiment_filter:
        return False
    if experiment_type_filter and run.experiment_type != experiment_type_filter.upper():
        return False
    return True


def _require(mapping: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if field not in mapping]
    if missing:
        raise ValueError(f"Missing required calibration experiment config field(s): {', '.join(missing)}")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping.")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list.")
    return value


def _int_list(value: Any, label: str) -> list[int]:
    return [int(item) for item in _list(value, label)]
