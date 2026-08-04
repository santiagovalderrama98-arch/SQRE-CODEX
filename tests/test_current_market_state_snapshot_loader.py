import pandas as pd

from sqre.current_market_state_snapshot_research.loader import CurrentMarketStateSnapshotResearchLoader


def test_loader_returns_empty_frame_for_missing_file(tmp_path):
    frame = CurrentMarketStateSnapshotResearchLoader.load_frame(tmp_path / "missing.csv")

    assert frame.empty


def test_loader_reads_existing_csv(tmp_path):
    path = tmp_path / "sample.csv"
    pd.DataFrame([{"A": 1}]).to_csv(path, index=False)

    frame = CurrentMarketStateSnapshotResearchLoader.load_frame(path)

    assert len(frame) == 1
