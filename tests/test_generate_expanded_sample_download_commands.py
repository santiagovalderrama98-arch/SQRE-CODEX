import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_CONFIG = ROOT / "configs" / "validation" / "eurusd_expanded_historical_samples.yaml"


def test_generate_commands_filters_by_timeframe():
    module = _load_module()
    config = module.load_sample_config(SAMPLES_CONFIG)

    commands = module.generate_commands(config, timeframe="H4")

    assert len(commands) == 4
    assert all("--timeframe H4" in command for command in commands)
    assert "EURUSD_H4_period_3.csv" in commands[0]
    assert "EURUSD_M5" not in "\n".join(commands)


def test_generate_commands_filters_by_sample_and_provider_override():
    module = _load_module()
    config = module.load_sample_config(SAMPLES_CONFIG)

    commands = module.generate_commands(config, provider="histdata", sample_id="eurusd_d1_period_4")

    assert len(commands) == 1
    assert "--provider histdata" in commands[0]
    assert "--timeframe D1" in commands[0]
    assert "--start 2004-01-01" in commands[0]
    assert "--output data/raw/EURUSD_D1_period_4.csv" in commands[0]


def test_generate_commands_missing_only_skips_existing_output(tmp_path):
    module = _load_module()
    existing_path = tmp_path / "existing.csv"
    existing_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")
    config = {
        "provider": "twelvedata",
        "samples": [
            {
                "sample_id": "existing",
                "symbol": "EURUSD",
                "timeframe": "M5",
                "start": "2026-01-01",
                "end": "2026-01-02",
                "output_path": str(existing_path),
            },
            {
                "sample_id": "missing",
                "symbol": "EURUSD",
                "timeframe": "H1",
                "start": "2026-01-01",
                "end": "2026-01-02",
                "output_path": str(tmp_path / "missing.csv"),
            },
        ],
    }

    commands = module.generate_commands(config, missing_only=True)

    assert len(commands) == 1
    assert "--timeframe H1" in commands[0]


def test_write_output_script_writes_executable_shell_script(tmp_path):
    module = _load_module()
    output_path = tmp_path / "downloads.sh"

    module.write_output_script(output_path, ["python3 scripts/download_market_data.py"])

    text = output_path.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "python3 scripts/download_market_data.py" in text
    assert os.access(output_path, os.X_OK)


def _load_module():
    path = ROOT / "scripts" / "generate_expanded_sample_download_commands.py"
    spec = importlib.util.spec_from_file_location("generate_expanded_sample_download_commands", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
