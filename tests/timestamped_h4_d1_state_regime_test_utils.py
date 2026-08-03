from pathlib import Path

import pandas as pd


def write_synchronized_fixture(path: Path, *, h4_rows: int = 72, d1_rows: int = 30) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _h4_frame(h4_rows).to_csv(path / "h4_normalized_ohlc.csv", index=False)
    _d1_frame(d1_rows).to_csv(path / "d1_from_h4_ohlc.csv", index=False)
    pd.DataFrame(
        {
            "H4_Candle_ID": [f"H4_{index:06d}" for index in range(1, min(h4_rows, 10) + 1)],
            "D1_Date": ["2026-07-01"] * min(h4_rows, 10),
        }
    ).to_csv(path / "h4_d1_candle_alignment_map.csv", index=False)
    pd.DataFrame(
        {
            "Symbol": ["EURUSD"],
            "H4_Timeframe": ["H4"],
            "D1_Timeframe": ["D1"],
            "H4_Row_Count": [h4_rows],
            "D1_Row_Count": [d1_rows],
        }
    ).to_csv(path / "h4_d1_synchronized_data_summary.csv", index=False)
    return path


def _h4_frame(rows: int) -> pd.DataFrame:
    dates = pd.date_range("2026-07-01 00:00:00", periods=rows, freq="4h")
    base = [1.1000 + index * 0.0004 for index in range(rows)]
    return pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d %H:%M:%S"),
            "Open": base,
            "High": [value + 0.0010 for value in base],
            "Low": [value - 0.0008 for value in base],
            "Close": [value + 0.0006 for value in base],
            "Volume": [0] * rows,
            "Symbol": ["EURUSD"] * rows,
            "Timeframe": ["H4"] * rows,
        }
    )


def _d1_frame(rows: int) -> pd.DataFrame:
    dates = pd.date_range("2026-07-01", periods=rows, freq="D")
    base = [1.1000 + index * 0.0012 for index in range(rows)]
    return pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d %H:%M:%S"),
            "D1_Period_Start": dates.strftime("%Y-%m-%d %H:%M:%S"),
            "D1_Period_End": (dates + pd.Timedelta(hours=20)).strftime("%Y-%m-%d %H:%M:%S"),
            "Open": base,
            "High": [value + 0.0020 for value in base],
            "Low": [value - 0.0015 for value in base],
            "Close": [value + 0.0010 for value in base],
            "Volume": [0] * rows,
            "Symbol": ["EURUSD"] * rows,
            "Timeframe": ["D1"] * rows,
        }
    )
