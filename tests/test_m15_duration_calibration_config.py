from pathlib import Path

from sqre.calibration_experiments.config import build_experiment_runs, load_calibration_experiment_config


CONFIG = Path("configs/validation/m15_duration_calibration_experiments.yaml")


def test_m15_duration_config_contains_only_m15_scenarios():
    config = load_calibration_experiment_config(CONFIG)

    scenario_ids = {scenario.scenario_id for scenario in config.base_scenarios}
    timeframes = {scenario.timeframe for scenario in config.base_scenarios}

    assert timeframes == {"M15"}
    assert len(scenario_ids) == 7
    assert scenario_ids == {f"eurusd_m15_period_{index}" for index in range(1, 8)}
    assert "eurusd_m5_period_8" not in scenario_ids
    assert not any("h1" in scenario_id or "h4" in scenario_id or "d1" in scenario_id for scenario_id in scenario_ids)


def test_m15_duration_config_builds_expected_duration_runs():
    config = load_calibration_experiment_config(CONFIG)
    runs = build_experiment_runs(config, Path("data/validation/m15_duration_calibration"))

    assert len(runs) == 35
    assert {run.experiment_type for run in runs} == {"DURATION"}
    assert {run.timeframe for run in runs} == {"M15"}
    assert {run.experiment_id for run in runs} == {
        "m15_duration_4h",
        "m15_duration_6h",
        "m15_duration_8h_baseline",
        "m15_duration_10h",
        "m15_duration_12h",
    }
    assert {run.max_structure_duration_seconds for run in runs} == {14400, 21600, 28800, 36000, 43200}
    assert len([run for run in runs if run.experiment_id == "m15_duration_8h_baseline"]) == 7
