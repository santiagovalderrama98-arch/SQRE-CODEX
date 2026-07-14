import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_CONFIG = ROOT / "configs" / "validation" / "eurusd_m15_historical_samples.yaml"


def test_m15_historical_sample_config_defines_seven_m15_samples():
    module = _load_generator_module()

    config = module.load_sample_config(SAMPLES_CONFIG)

    assert config["sample_set_name"] == "eurusd_m15_historical_samples_v1"
    assert config["symbol"] == "EURUSD"
    assert config["provider"] == "twelvedata"
    assert config["pip_size"] == 0.0001
    assert len(config["samples"]) == 7
    assert {sample["timeframe"] for sample in config["samples"]} == {"M15"}


def test_m15_historical_sample_config_uses_expected_periods_and_paths():
    module = _load_generator_module()

    config = module.load_sample_config(SAMPLES_CONFIG)
    samples = {sample["sample_id"]: sample for sample in config["samples"]}

    assert set(samples) == {f"eurusd_m15_period_{index}" for index in range(1, 8)}
    assert str(samples["eurusd_m15_period_1"]["start"]) == "2026-06-01"
    assert str(samples["eurusd_m15_period_1"]["end"]) == "2026-06-30"
    assert str(samples["eurusd_m15_period_7"]["start"]) == "2025-09-01"
    assert str(samples["eurusd_m15_period_7"]["end"]) == "2025-09-30"
    assert all(str(sample["output_path"]).startswith("data/raw/EURUSD_M15_period_") for sample in samples.values())
    assert "eurusd_m5_period_8" not in samples


def _load_generator_module():
    path = ROOT / "scripts" / "generate_expanded_sample_download_commands.py"
    spec = importlib.util.spec_from_file_location("generate_expanded_sample_download_commands", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
