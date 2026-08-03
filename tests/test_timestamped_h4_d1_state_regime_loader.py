from pathlib import Path

import pandas as pd

from sqre.timestamped_h4_d1_state_regime_generation.loader import load_h4_ohlc
from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_loader_reads_normalized_h4_ohlc(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync", h4_rows=12, d1_rows=5)

    frame = load_h4_ohlc(input_dir)

    assert len(frame) == 12
    assert list(frame.columns) == ["Date", "Open", "High", "Low", "Close", "Volume", "Symbol", "Timeframe"]
    assert pd.api.types.is_datetime64_any_dtype(frame["Date"])


def test_loader_defaults_missing_volume_to_zero(tmp_path: Path):
    input_dir = tmp_path / "sync"
    input_dir.mkdir()
    pd.DataFrame(
        {
            "Date": ["2026-07-01 00:00:00", "2026-07-01 04:00:00"],
            "Open": [1.0, 1.1],
            "High": [1.2, 1.3],
            "Low": [0.9, 1.0],
            "Close": [1.1, 1.2],
        }
    ).to_csv(input_dir / "h4_normalized_ohlc.csv", index=False)

    frame = load_h4_ohlc(input_dir)

    assert frame["Volume"].tolist() == [0, 0]


def test_loader_returns_empty_for_missing_required_columns(tmp_path: Path):
    input_dir = tmp_path / "sync"
    input_dir.mkdir()
    pd.DataFrame({"Date": ["2026-07-01"], "Open": [1]}).to_csv(input_dir / "h4_normalized_ohlc.csv", index=False)

    frame = load_h4_ohlc(input_dir)

    assert frame.empty
