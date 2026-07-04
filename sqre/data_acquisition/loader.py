from pathlib import Path

import pandas as pd


class DataLoader:
    def load_csv(self, path: Path | str) -> pd.DataFrame:
        data = pd.read_csv(Path(path))
        if "Date" in data.columns:
            data["Date"] = pd.to_datetime(data["Date"], errors="raise")
        return data
