from __future__ import annotations

import pytest

from sqre.market_states.config import MarketStatesConfig
from sqre.market_states.config_loader import load_market_state_config_from_yaml


def test_load_baseline_profile_preserves_defaults() -> None:
    config = load_market_state_config_from_yaml("configs/validation/state_threshold_profiles.yaml", "state_baseline")

    assert config == MarketStatesConfig()


def test_load_profile_overrides_thresholds() -> None:
    config = load_market_state_config_from_yaml("configs/validation/state_threshold_profiles.yaml", "directional_stricter")

    assert config.directional_displacement_efficiency_threshold == 0.65
    assert config.directional_displacement_confidence_threshold == 0.60


def test_load_timeframe_override() -> None:
    config = load_market_state_config_from_yaml(
        "configs/validation/state_threshold_profiles.yaml",
        "balanced_high_tf",
        timeframe="D1",
    )

    assert config.directional_displacement_efficiency_threshold == 0.68
    assert config.directional_displacement_confidence_threshold == 0.62


def test_supports_alias_for_event_density_threshold(tmp_path) -> None:
    config_path = tmp_path / "profiles.yaml"
    config_path.write_text(
        """
profiles:
  - profile_id: alias_profile
    overrides:
      complex_consolidation_event_density_threshold: 0.36
""",
        encoding="utf-8",
    )

    config = load_market_state_config_from_yaml(config_path, "alias_profile")

    assert config.complex_consolidation_density_threshold == 0.36


def test_unknown_profile_raises() -> None:
    with pytest.raises(ValueError, match="Unknown Market State threshold profile_id"):
        load_market_state_config_from_yaml("configs/validation/state_threshold_profiles.yaml", "missing")


def test_unknown_override_key_raises(tmp_path) -> None:
    config_path = tmp_path / "profiles.yaml"
    config_path.write_text(
        """
profiles:
  - profile_id: bad_profile
    overrides:
      unknown_threshold: 0.4
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown Market State threshold override key"):
        load_market_state_config_from_yaml(config_path, "bad_profile")
