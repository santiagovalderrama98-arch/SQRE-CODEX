from pathlib import Path

from sqre.timestamped_h4_d1_state_regime_generation.loader import load_h4_ohlc
from sqre.timestamped_h4_d1_state_regime_generation.timeframe_pipeline_adapter import (
    build_timestamped_state_candidates,
)
from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_pipeline_adapter_builds_timestamped_state_candidates(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync", h4_rows=24, d1_rows=5)
    frame = load_h4_ohlc(input_dir)

    rows = build_timestamped_state_candidates(
        frame,
        symbol="EURUSD",
        timeframe="H4",
        window_size=12,
        state_prefix="H4_STATE",
    )

    assert len(rows) == 2
    assert rows["State_ID"].tolist() == ["H4_STATE_000001", "H4_STATE_000002"]
    assert rows["State_Start_Time"].notna().all()
    assert rows["Market_State"].notna().all()
