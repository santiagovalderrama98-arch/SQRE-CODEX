from pathlib import Path

from sqre.timestamped_h4_d1_state_regime_generation.h4_state_table_builder import H4_STATE_COLUMNS, build_h4_state_table
from sqre.timestamped_h4_d1_state_regime_generation.loader import load_h4_ohlc
from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_h4_state_table_uses_required_columns(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync", h4_rows=24, d1_rows=5)
    frame = load_h4_ohlc(input_dir)

    states = build_h4_state_table(frame, symbol="EURUSD", timeframe="H4", window_size=12)

    assert list(states.columns) == H4_STATE_COLUMNS
    assert len(states) == 2
    assert states["H4_State_ID"].str.startswith("H4_STATE_").all()
