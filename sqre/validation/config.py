"""Configuration loading for SQRE validation scenarios."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from sqre.validation.models import ValidationConfig, ValidationScenario


def load_validation_config(
    path: Path | str,
    *,
    output_dir: Path | str = Path("data/validation"),
    scenario_id: str | None = None,
) -> ValidationConfig:
    """Load validation YAML config.

    PyYAML is used when available. A small fallback parser supports SQRE's
    simple config format so local validation still works in lean environments.
    """

    config_path = Path(path)
    raw = _load_yaml_like(config_path)
    required = ["validation_name", "symbol", "pip_size", "minimum_sample_size", "scenarios"]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Validation config is missing required keys: {', '.join(missing)}")

    output_root = Path(output_dir)
    scenarios = [
        _scenario_from_dict(item, raw, output_root)
        for item in raw["scenarios"]
        if scenario_id is None or item.get("scenario_id") == scenario_id
    ]
    if scenario_id is not None and not scenarios:
        raise ValueError(f"Scenario not found in validation config: {scenario_id}")

    return ValidationConfig(
        validation_name=str(raw["validation_name"]),
        symbol=str(raw["symbol"]),
        pip_size=float(raw["pip_size"]),
        minimum_sample_size=int(raw["minimum_sample_size"]),
        scenarios=scenarios,
    )


def _scenario_from_dict(data: dict[str, Any], root: dict[str, Any], output_root: Path) -> ValidationScenario:
    required = ["scenario_id", "symbol", "timeframe", "ohlc_path", "max_structure_duration_seconds", "forward_candles"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Validation scenario is missing required keys: {', '.join(missing)}")
    candles = [int(item) for item in data["forward_candles"]]
    if not candles:
        raise ValueError(f"Scenario {data['scenario_id']} must define at least one forward candle window")
    return ValidationScenario(
        scenario_id=str(data["scenario_id"]),
        symbol=str(data["symbol"]),
        timeframe=str(data["timeframe"]),
        ohlc_path=Path(str(data["ohlc_path"])),
        max_structure_duration_seconds=int(data["max_structure_duration_seconds"]),
        forward_candles=candles,
        pip_size=float(root["pip_size"]),
        minimum_sample_size=int(root["minimum_sample_size"]),
        output_root=output_root,
    )


def _load_yaml_like(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if not isinstance(loaded, dict):
            raise ValueError("Validation config root must be a mapping")
        return loaded
    except ModuleNotFoundError:
        return _parse_simple_validation_yaml(text)


def _parse_simple_validation_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    scenarios: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line == "scenarios:":
            result["scenarios"] = scenarios
            continue
        if line.startswith("  - "):
            current = {}
            scenarios.append(current)
            key, value = _split_key_value(line[4:])
            current[key] = _parse_scalar(value)
            continue
        if line.startswith("    "):
            if current is None:
                raise ValueError("Scenario property found before a scenario item")
            key, value = _split_key_value(line.strip())
            current[key] = _parse_scalar(value)
            continue
        key, value = _split_key_value(line.strip())
        result[key] = _parse_scalar(value)

    if "scenarios" not in result:
        result["scenarios"] = scenarios
    return result


def _split_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Invalid validation config line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _parse_scalar(value: str) -> object:
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value.strip('"').strip("'")
