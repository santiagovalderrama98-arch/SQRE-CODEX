from collections import Counter
from pathlib import Path

from sqre.validation.config import load_validation_config


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_CONFIG = ROOT / "configs" / "validation" / "eurusd_m15_validation.yaml"


def test_m15_validation_config_loads_expected_scenarios(tmp_path):
    config = load_validation_config(VALIDATION_CONFIG, output_dir=tmp_path / "validation")

    assert config.validation_name == "eurusd_m15_introduction_validation"
    assert config.symbol == "EURUSD"
    assert config.pip_size == 0.0001
    assert config.minimum_sample_size == 5
    assert len(config.scenarios) == 7


def test_m15_validation_config_uses_m15_duration_and_forward_windows(tmp_path):
    config = load_validation_config(VALIDATION_CONFIG, output_dir=tmp_path / "validation")

    assert Counter(scenario.timeframe for scenario in config.scenarios) == {"M15": 7}
    assert all(scenario.max_structure_duration_seconds == 28800 for scenario in config.scenarios)
    assert all(scenario.forward_candles == [3, 6, 12] for scenario in config.scenarios)
    assert {scenario.scenario_id for scenario in config.scenarios} == {f"eurusd_m15_period_{index}" for index in range(1, 8)}
    assert not any("m5_period_8" in scenario.scenario_id for scenario in config.scenarios)
