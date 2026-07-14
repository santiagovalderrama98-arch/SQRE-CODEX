from pathlib import Path

from sqre.calibration_experiments.config import build_experiment_runs, load_calibration_experiment_config


def test_h1_m5_duration_config_contains_only_expected_timeframes_and_scenarios():
    config = load_calibration_experiment_config(Path("configs/validation/h1_m5_duration_calibration_experiments.yaml"))

    scenario_ids = {scenario.scenario_id for scenario in config.base_scenarios}
    timeframes = {scenario.timeframe for scenario in config.base_scenarios}

    assert timeframes == {"H1", "M5"}
    assert "eurusd_m5_period_8" not in scenario_ids
    assert not any("h4" in scenario_id for scenario_id in scenario_ids)
    assert not any("d1" in scenario_id for scenario_id in scenario_ids)
    assert len([scenario for scenario in config.base_scenarios if scenario.timeframe == "H1"]) == 7
    assert len([scenario for scenario in config.base_scenarios if scenario.timeframe == "M5"]) == 7


def test_h1_m5_duration_config_builds_expected_duration_runs():
    config = load_calibration_experiment_config(Path("configs/validation/h1_m5_duration_calibration_experiments.yaml"))
    runs = build_experiment_runs(config, Path("data/validation/h1_m5_duration_calibration"))

    assert len(runs) == 49
    assert {run.experiment_type for run in runs} == {"DURATION"}
    assert len([run for run in runs if run.timeframe == "H1"]) == 21
    assert len([run for run in runs if run.timeframe == "M5"]) == 28
    assert {run.max_structure_duration_seconds for run in runs if run.timeframe == "H1"} == {64800, 86400, 108000}
    assert {run.max_structure_duration_seconds for run in runs if run.timeframe == "M5"} == {7200, 10800, 14400, 21600}
