from __future__ import annotations

import pytest
import pandas as pd

from sqre.data_acquisition.storage import MarketDataStorage


def test_storage_saves_csv_and_creates_parent_dirs(tmp_path) -> None:
    data = pd.DataFrame({"Date": ["2020-01-01"], "Open": [1], "High": [1], "Low": [1], "Close": [1], "Volume": [0]})
    storage = MarketDataStorage(tmp_path / "raw")

    path = storage.save(data, "eurusd", "m1")

    assert path.exists()
    assert path.name == "EURUSD_M1.csv"


def test_storage_avoids_overwriting_existing_files(tmp_path) -> None:
    data = pd.DataFrame({"Date": ["2020-01-01"], "Open": [1], "High": [1], "Low": [1], "Close": [1], "Volume": [0]})
    storage = MarketDataStorage(tmp_path)
    storage.save(data, "EURUSD", "M1")

    with pytest.raises(FileExistsError):
        storage.save(data, "EURUSD", "M1")
