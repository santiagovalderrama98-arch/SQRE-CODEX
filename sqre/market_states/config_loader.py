"""YAML config loader for optional Market State threshold profiles."""

from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
from typing import Any

from sqre.market_states.config import MarketStatesConfig


_FIELD_NAMES = {field.name for field in fields(MarketStatesConfig)}
_ALIASES = {
    "complex_consolidation_event_density_threshold": "complex_consolidation_density_threshold",
}


def load_market_state_config_from_yaml(
    path: Path | str,
    profile_id: str | None = None,
    timeframe: str | None = None,
) -> MarketStatesConfig:
    """Load a MarketStatesConfig from a named YAML threshold profile."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Market state config file not found: {config_path}")
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to load Market State threshold profiles.") from exc
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Market State threshold profile file must be a YAML mapping.")
    profiles = raw.get("profiles")
    if not isinstance(profiles, list):
        raise ValueError("Market State threshold profile file must define a profiles list.")
    selected = _select_profile(profiles, profile_id)
    config = MarketStatesConfig()
    config = _apply_overrides(config, selected.get("overrides", {}), label=f"profile {selected['profile_id']}")
    timeframe_overrides = selected.get("timeframe_overrides", {})
    if timeframe and isinstance(timeframe_overrides, dict) and timeframe in timeframe_overrides:
        config = _apply_overrides(
            config,
            timeframe_overrides[timeframe],
            label=f"profile {selected['profile_id']} timeframe {timeframe}",
        )
    return config


def _select_profile(profiles: list[Any], profile_id: str | None) -> dict[str, Any]:
    normalized_profiles = [_profile_mapping(profile) for profile in profiles]
    if profile_id is None:
        return normalized_profiles[0]
    for profile in normalized_profiles:
        if profile["profile_id"] == profile_id:
            return profile
    raise ValueError(f"Unknown Market State threshold profile_id: {profile_id}")


def _profile_mapping(profile: Any) -> dict[str, Any]:
    if not isinstance(profile, dict):
        raise ValueError("Each Market State threshold profile must be a mapping.")
    if "profile_id" not in profile:
        raise ValueError("Each Market State threshold profile must include profile_id.")
    return profile


def _apply_overrides(config: MarketStatesConfig, overrides: Any, *, label: str) -> MarketStatesConfig:
    if overrides is None:
        overrides = {}
    if not isinstance(overrides, dict):
        raise ValueError(f"Overrides for {label} must be a mapping.")
    values: dict[str, float] = {}
    for raw_key, raw_value in overrides.items():
        key = _ALIASES.get(str(raw_key), str(raw_key))
        if key not in _FIELD_NAMES:
            raise ValueError(f"Unknown Market State threshold override key in {label}: {raw_key}")
        values[key] = float(raw_value)
    return replace(config, **values)
