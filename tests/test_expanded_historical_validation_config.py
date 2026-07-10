import importlib.util
from collections import Counter
from pathlib import Path

from sqre.validation.config import load_validation_config


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_CONFIG = ROOT / "configs" / "validation" / "eurusd_expanded_historical_samples.yaml"
VALIDATION_CONFIG = ROOT / "configs" / "validation" / "eurusd_expanded_historical_validation.yaml"


def test_expanded_historical_validation_config_loads_all_scenarios(tmp_path):
    config = load_validation_config(VALIDATION_CONFIG, output_dir=tmp_path / "validation")

    assert config.validation_name == "eurusd_expanded_historical_validation"
    assert config.symbol == "EURUSD"
    assert config.pip_size == 0.0001
    assert config.minimum_sample_size == 5
    assert len(config.scenarios) == 25


def test_expanded_historical_validation_config_includes_all_new_samples(tmp_path):
    sample_config = _load_generator_module().load_sample_config(SAMPLES_CONFIG)
    expected_sample_ids = {sample["sample_id"] for sample in sample_config["samples"]}

    config = load_validation_config(VALIDATION_CONFIG, output_dir=tmp_path / "validation")
    scenario_ids = {scenario.scenario_id for scenario in config.scenarios}

    assert expected_sample_ids <= scenario_ids


def test_expanded_historical_validation_config_uses_expected_timeframe_settings(tmp_path):
    config = load_validation_config(VALIDATION_CONFIG, output_dir=tmp_path / "validation")

    counts = Counter(scenario.timeframe for scenario in config.scenarios)
    assert counts == {"M5": 8, "H1": 7, "H4": 6, "D1": 4}
    assert all(scenario.forward_candles == [3, 6, 12] for scenario in config.scenarios)
    assert _duration(config.scenarios, "M5") == {14400}
    assert _duration(config.scenarios, "H1") == {86400}
    assert _duration(config.scenarios, "H4") == {604800}
    assert _duration(config.scenarios, "D1") == {2592000}


def _duration(scenarios, timeframe: str) -> set[int]:
    return {scenario.max_structure_duration_seconds for scenario in scenarios if scenario.timeframe == timeframe}


def _load_generator_module():
    path = ROOT / "scripts" / "generate_expanded_sample_download_commands.py"
    spec = importlib.util.spec_from_file_location("generate_expanded_sample_download_commands", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
