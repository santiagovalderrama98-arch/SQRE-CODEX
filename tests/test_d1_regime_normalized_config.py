from sqre.d1_regime_normalized_research.config import load_d1_regime_research_config


def test_config_includes_only_four_d1_regimes():
    config = load_d1_regime_research_config("configs/validation/d1_regime_normalized_research.yaml")

    assert config.timeframe == "D1"
    assert len(config.scenarios) == 4
    assert {scenario.timeframe for scenario in config.scenarios} == {"D1"}
    assert len({scenario.regime_id for scenario in config.scenarios}) == 4
    assert not any("h4" in scenario.scenario_id.lower() for scenario in config.scenarios)


def test_config_defaults_are_research_defaults():
    config = load_d1_regime_research_config("configs/validation/d1_regime_normalized_research.yaml")

    assert config.minimum_sample_size == 5
    assert config.high_regime_sensitivity_threshold == 0.35
    assert config.moderate_regime_sensitivity_threshold == 0.20
    assert config.forward_range_stability_threshold == 0.30
    assert config.minimum_regime_count == 2
