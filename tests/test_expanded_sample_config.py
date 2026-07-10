import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_CONFIG = ROOT / "configs" / "validation" / "eurusd_expanded_historical_samples.yaml"


def test_expanded_sample_config_defines_expected_sample_set():
    module = _load_generator_module()

    config = module.load_sample_config(SAMPLES_CONFIG)

    assert config["sample_set_name"] == "eurusd_expanded_historical_samples_v1"
    assert config["symbol"] == "EURUSD"
    assert config["provider"] == "twelvedata"
    assert config["pip_size"] == 0.0001
    assert len(config["samples"]) == 18


def test_expanded_sample_config_has_expected_timeframe_counts_and_paths():
    module = _load_generator_module()

    config = module.load_sample_config(SAMPLES_CONFIG)
    samples = config["samples"]

    assert _count(samples, "M5") == 6
    assert _count(samples, "H1") == 6
    assert _count(samples, "H4") == 4
    assert _count(samples, "D1") == 2
    assert len({sample["sample_id"] for sample in samples}) == 18
    assert all(str(sample["output_path"]).startswith("data/raw/EURUSD_") for sample in samples)
    assert all(str(sample["output_path"]).endswith(".csv") for sample in samples)


def test_expanded_sample_config_includes_required_historical_windows():
    module = _load_generator_module()

    config = module.load_sample_config(SAMPLES_CONFIG)
    by_id = {sample["sample_id"]: sample for sample in config["samples"]}

    assert str(by_id["eurusd_m5_period_3"]["start"]) == "2026-05-01"
    assert str(by_id["eurusd_m5_period_8"]["end"]) == "2025-06-15"
    assert str(by_id["eurusd_h1_period_7"]["start"]) == "2025-01-01"
    assert str(by_id["eurusd_h4_period_3"]["end"]) == "2023-06-30"
    assert str(by_id["eurusd_d1_period_4"]["start"]) == "2004-01-01"


def _count(samples: list[dict[str, object]], timeframe: str) -> int:
    return sum(1 for sample in samples if sample["timeframe"] == timeframe)


def _load_generator_module():
    path = ROOT / "scripts" / "generate_expanded_sample_download_commands.py"
    spec = importlib.util.spec_from_file_location("generate_expanded_sample_download_commands", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
