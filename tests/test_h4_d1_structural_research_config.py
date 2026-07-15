from sqre.validation.config import load_validation_config


def test_config_includes_only_h4_and_d1_scenarios():
    config = load_validation_config("configs/validation/h4_d1_structural_research_validation.yaml")

    timeframes = {scenario.timeframe for scenario in config.scenarios}

    assert timeframes == {"H4", "D1"}
    assert len([scenario for scenario in config.scenarios if scenario.timeframe == "H4"]) == 4
    assert len([scenario for scenario in config.scenarios if scenario.timeframe == "D1"]) == 4


def test_config_excludes_intraday_and_partial_samples():
    config = load_validation_config("configs/validation/h4_d1_structural_research_validation.yaml")
    scenario_ids = {scenario.scenario_id for scenario in config.scenarios}

    assert not any("m5" in scenario_id for scenario_id in scenario_ids)
    assert not any("m15" in scenario_id for scenario_id in scenario_ids)
    assert not any("h1" in scenario_id for scenario_id in scenario_ids)
    assert "eurusd_h4_period_5" not in scenario_ids
    assert "eurusd_h4_period_6" not in scenario_ids
