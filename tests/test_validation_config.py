from pathlib import Path

from sqre.validation.config import load_validation_config


def test_load_validation_config_filters_scenario(tmp_path):
    config_path = tmp_path / "validation.yaml"
    config_path.write_text(
        """
validation_name: sample_validation
symbol: EURUSD
pip_size: 0.0001
minimum_sample_size: 5

scenarios:
  - scenario_id: eurusd_m5
    symbol: EURUSD
    timeframe: M5
    ohlc_path: data/raw/EURUSD_M5.csv
    max_structure_duration_seconds: 14400
    forward_candles: [3, 6, 12]

  - scenario_id: eurusd_h1
    symbol: EURUSD
    timeframe: H1
    ohlc_path: data/raw/EURUSD_H1.csv
    max_structure_duration_seconds: 86400
    forward_candles: [3, 6, 12]
""",
        encoding="utf-8",
    )

    config = load_validation_config(config_path, output_dir=tmp_path / "validation", scenario_id="eurusd_h1")

    assert config.validation_name == "sample_validation"
    assert len(config.scenarios) == 1
    scenario = config.scenarios[0]
    assert scenario.scenario_id == "eurusd_h1"
    assert scenario.ohlc_path == Path("data/raw/EURUSD_H1.csv")
    assert scenario.processed_dir == tmp_path / "validation" / "eurusd_h1" / "processed"
