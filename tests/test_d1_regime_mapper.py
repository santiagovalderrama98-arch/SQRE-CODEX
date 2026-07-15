from sqre.d1_regime_normalized_research.config import load_d1_regime_research_config
from sqre.d1_regime_normalized_research.regime_mapper import build_regime_lookup, map_scenario_to_regime


def test_regime_mapper_maps_each_d1_scenario():
    config = load_d1_regime_research_config("configs/validation/d1_regime_normalized_research.yaml")

    lookup = build_regime_lookup(config)

    assert lookup["eurusd_d1_period_1"].regime_id == "D1_REGIME_2021_2026"
    assert lookup["eurusd_d1_period_4"].regime_label == "2004_2009_early_history_regime"
    assert map_scenario_to_regime(config, "eurusd_d1_period_2").regime_id == "D1_REGIME_2015_2020"
