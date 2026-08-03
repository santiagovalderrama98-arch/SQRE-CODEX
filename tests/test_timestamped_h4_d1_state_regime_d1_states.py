from pathlib import Path

from sqre.timestamped_h4_d1_state_regime_generation.d1_state_regime_table_builder import (
    D1_STATE_COLUMNS,
    build_d1_state_regime_table,
)
from sqre.timestamped_h4_d1_state_regime_generation.loader import load_d1_ohlc
from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_d1_state_regime_table_uses_required_columns(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync", h4_rows=24, d1_rows=10)
    frame = load_d1_ohlc(input_dir)

    states = build_d1_state_regime_table(frame, symbol="EURUSD", timeframe="D1", window_size=5)

    assert list(states.columns) == D1_STATE_COLUMNS
    assert len(states) == 2
    assert states["D1_State_ID"].str.startswith("D1_STATE_").all()
    assert states["Regime_Label"].str.startswith("D1_").all()
