from __future__ import annotations

import pytest

from sqre.state_threshold_experiments.config import build_experiment_runs, load_state_threshold_experiment_config


def _write_config(path) -> None:
    path.write_text(
        """
experiment_name: test_state_thresholds
symbol: EURUSD
pip_size: 0.0001
forward_candles: [3, 6]
minimum_sample_size: 5
baseline_max_structure_duration_seconds:
  H4: 604800
state_config_path: configs/validation/state_threshold_profiles.yaml
base_scenarios:
  - scenario_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
    ohlc_path: data/raw/EURUSD_H4_period_1.csv
profiles:
  - state_baseline
  - directional_stricter
""",
        encoding="utf-8",
    )


def test_load_state_threshold_experiment_config(tmp_path) -> None:
    config_path = tmp_path / "experiments.yaml"
    _write_config(config_path)

    config = load_state_threshold_experiment_config(config_path)

    assert config.experiment_name == "test_state_thresholds"
    assert config.forward_candles == [3, 6]
    assert len(config.base_scenarios) == 1
    assert config.profiles == ["state_baseline", "directional_stricter"]


def test_build_experiment_runs_crosses_profiles_and_scenarios(tmp_path) -> None:
    config_path = tmp_path / "experiments.yaml"
    _write_config(config_path)
    config = load_state_threshold_experiment_config(config_path)

    runs = build_experiment_runs(config, tmp_path / "validation")

    assert [run.experiment_run_id for run in runs] == [
        "state_baseline__eurusd_h4_period_1",
        "directional_stricter__eurusd_h4_period_1",
    ]
    assert runs[0].max_structure_duration_seconds == 604800
    assert runs[0].processed_dir == tmp_path / "validation/state_baseline/eurusd_h4_period_1/processed"


def test_build_experiment_runs_supports_filters(tmp_path) -> None:
    config_path = tmp_path / "experiments.yaml"
    _write_config(config_path)
    config = load_state_threshold_experiment_config(config_path)

    runs = build_experiment_runs(
        config,
        tmp_path / "validation",
        profile_filter="directional_stricter",
        scenario_filter="eurusd_h4_period_1",
    )

    assert len(runs) == 1
    assert runs[0].experiment_run_id == "directional_stricter__eurusd_h4_period_1"


def test_missing_required_config_field_raises(tmp_path) -> None:
    config_path = tmp_path / "experiments.yaml"
    config_path.write_text("experiment_name: bad\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required state threshold experiment config field"):
        load_state_threshold_experiment_config(config_path)
