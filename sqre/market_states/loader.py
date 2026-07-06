"""Load Market Structure outputs for Market States."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.market_states.models import StructuralInput


class MarketStatesLoader:
    """Load and validate structures.csv files."""

    _REQUIRED_COLUMNS = {
        "Structure_ID",
        "Symbol",
        "Timeframe",
        "Start_Time",
        "End_Time",
        "Direction",
        "Lifecycle_Stage",
        "Persistence_Index",
        "Structural_Complexity",
        "Structural_Stability",
        "Structural_Efficiency",
        "Event_Density",
        "Structural_Volatility",
        "Structural_Symmetry",
        "Structural_Confidence",
    }

    def load(self, path: Path | str) -> list[StructuralInput]:
        frame = self.load_frame(path)
        return [self._row_to_structure(row) for _, row in frame.iterrows()]

    def load_frame(self, path: Path | str) -> pd.DataFrame:
        frame = pd.read_csv(Path(path))
        self._validate_columns(frame)
        frame = frame.copy()
        frame["Start_Time"] = pd.to_datetime(frame["Start_Time"], errors="raise")
        frame["End_Time"] = pd.to_datetime(frame["End_Time"], errors="raise")
        frame["Direction"] = frame["Direction"].astype(str).str.strip().str.upper()
        frame["Lifecycle_Stage"] = frame["Lifecycle_Stage"].astype(str).str.strip().str.upper()
        return frame.sort_values("Start_Time").reset_index(drop=True)

    def _validate_columns(self, frame: pd.DataFrame) -> None:
        missing = sorted(self._REQUIRED_COLUMNS - set(frame.columns))
        if missing:
            raise ValueError(f"Missing required structure columns: {', '.join(missing)}")

    def _row_to_structure(self, row: pd.Series) -> StructuralInput:
        return StructuralInput(
            structure_id=str(row["Structure_ID"]),
            symbol=str(row["Symbol"]),
            timeframe=str(row["Timeframe"]),
            start_time=row["Start_Time"].to_pydatetime(),
            end_time=row["End_Time"].to_pydatetime(),
            direction=str(row["Direction"]),
            lifecycle_stage=str(row["Lifecycle_Stage"]),
            persistence_index=float(row["Persistence_Index"]),
            structural_complexity=float(row["Structural_Complexity"]),
            structural_stability=float(row["Structural_Stability"]),
            structural_efficiency=float(row["Structural_Efficiency"]),
            event_density=float(row["Event_Density"]),
            structural_volatility=float(row["Structural_Volatility"]),
            structural_symmetry=float(row["Structural_Symmetry"]),
            structural_confidence=float(row["Structural_Confidence"]),
            duration_seconds=self._optional_float(row, "Duration_Seconds"),
            price_displacement=self._optional_float(row, "Price_Displacement"),
            event_count=self._optional_int(row, "Event_Count"),
            leg_count=self._optional_int(row, "Leg_Count"),
        )

    def _optional_float(self, row: pd.Series, column: str) -> float | None:
        if column not in row.index or pd.isna(row[column]):
            return None
        return float(row[column])

    def _optional_int(self, row: pd.Series, column: str) -> int | None:
        if column not in row.index or pd.isna(row[column]):
            return None
        return int(row[column])
