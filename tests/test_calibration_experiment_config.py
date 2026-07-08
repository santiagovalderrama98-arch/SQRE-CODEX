from pathlib import Path

import pytest

from sqre.calibration_experiments.config import build_experiment_runs, load_calibration_experiment_config


def _write_config(path: Path) -> None:
    path.write_text(
        """
experiment_name: calibration_experiments_v1
symbol: EURUSD
pip_size: 0.0001
forward_candles: [3, 6, 12]
base_scenarios:
  - scenario_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
    ohlc_path: data/raw/EURUSD_H4_period_1.csv
duration_experiments:
  - experiment_id: duration_baseline
    description: Current baseline structural duration limits
    max_structure_duration_seconds:
      H4: 604800
sample_size_experiments:
  - experiment_id: sample_size_5
    description: Baseline minimum sample size
    minimum_sample_size: 5
""",
        encoding="utf-8",
    )


def test_valid_config_loads(tmp_path: Path):
    config_path = tmp_path / "calibration_experiments.yaml"
    _write_config(config_path)

    config = load_calibration_experiment_config(config_path)

    assert config.experiment_name == "calibration_experiments_v1"
    assert config.base_scenarios[0].scenario_id == "eurusd_h4_period_1"
    assert config.duration_experiments[0].max_structure_duration_seconds_by_timeframe["H4"] == 604800
    assert config.sample_size_experiments[0].minimum_sample_size == 5


def test_missing_required_top_level_field_fails(tmp_path: Path):
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("symbol: EURUSD\n", encoding="utf-8")

    with pytest.raises(ValueError, match="experiment_name"):
        load_calibration_experiment_config(config_path)


def test_missing_scenario_field_fails(tmp_path: Path):
    config_path = tmp_path / "bad.yaml"
    _write_config(config_path)
    text = config_path.read_text(encoding="utf-8").replace("    ohlc_path: data/raw/EURUSD_H4_period_1.csv\n", "")
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match="ohlc_path"):
        load_calibration_experiment_config(config_path)


def test_build_experiment_runs_creates_expected_ids_and_filters(tmp_path: Path):
    config_path = tmp_path / "calibration_experiments.yaml"
    _write_config(config_path)
    config = load_calibration_experiment_config(config_path)

    runs = build_experiment_runs(config, tmp_path / "out")
    duration_runs = build_experiment_runs(config, tmp_path / "out", experiment_type_filter="DURATION")
    scenario_runs = build_experiment_runs(config, tmp_path / "out", scenario_filter="eurusd_h4_period_1")
    experiment_runs = build_experiment_runs(config, tmp_path / "out", experiment_filter="sample_size_5")

    assert [run.experiment_run_id for run in runs] == [
        "duration_baseline__eurusd_h4_period_1",
        "sample_size_5__eurusd_h4_period_1",
    ]
    assert len(duration_runs) == 1
    assert len(scenario_runs) == 2
    assert len(experiment_runs) == 1
    assert experiment_runs[0].experiment_type == "SAMPLE_SIZE"
