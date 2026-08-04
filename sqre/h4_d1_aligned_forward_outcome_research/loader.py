"""Load inputs for H4/D1 aligned forward outcome research."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


TRANSITION_ALIGNMENT_COLUMNS = [
    "H4_D1_Transition_Alignment_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_ID",
    "H4_Transition_Time",
    "H4_Transition_Label",
    "H4_Source_State",
    "H4_Target_State",
    "D1_State_ID",
    "D1_Date",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
]

H4_OHLC_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


def expected_input_paths(
    same_time_alignment_dir: Path,
    synchronized_data_dir: Path,
    contextual_transition_dir: Path,
) -> dict[str, Path]:
    return {
        "h4_transition_d1_same_time_alignment": same_time_alignment_dir
        / "h4_transition_d1_same_time_alignment.csv",
        "h4_state_d1_same_time_alignment": same_time_alignment_dir / "h4_state_d1_same_time_alignment.csv",
        "h4_d1_same_time_alignment_summary": same_time_alignment_dir / "h4_d1_same_time_alignment_summary.csv",
        "h4_normalized_ohlc": synchronized_data_dir / "h4_normalized_ohlc.csv",
        "d1_from_h4_ohlc": synchronized_data_dir / "d1_from_h4_ohlc.csv",
        "h4_d1_candle_alignment_map": synchronized_data_dir / "h4_d1_candle_alignment_map.csv",
        "h4_d1_synchronized_data_summary": synchronized_data_dir / "h4_d1_synchronized_data_summary.csv",
        "h4_d1_same_time_contextual_transition_profiles": contextual_transition_dir
        / "h4_d1_same_time_contextual_transition_profiles.csv",
        "h4_d1_context_sample_adequacy_review": contextual_transition_dir
        / "h4_d1_context_sample_adequacy_review.csv",
        "h4_d1_same_time_contextual_transition_review_summary": contextual_transition_dir
        / "h4_d1_same_time_contextual_transition_review_summary.csv",
    }


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(resolved)
    except (EmptyDataError, ParserError):
        return pd.DataFrame()


def load_transition_alignment(same_time_alignment_dir: Path) -> pd.DataFrame:
    frame = read_optional_csv(same_time_alignment_dir / "h4_transition_d1_same_time_alignment.csv")
    return _normalize_transition_alignment(frame)


def load_h4_ohlc(synchronized_data_dir: Path) -> pd.DataFrame:
    frame = read_optional_csv(synchronized_data_dir / "h4_normalized_ohlc.csv")
    return _normalize_h4_ohlc(frame)


def load_contextual_profiles(contextual_transition_dir: Path) -> pd.DataFrame:
    return read_optional_csv(contextual_transition_dir / "h4_d1_same_time_contextual_transition_profiles.csv")


def _normalize_transition_alignment(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=TRANSITION_ALIGNMENT_COLUMNS)
    normalized = frame.copy()
    for column in TRANSITION_ALIGNMENT_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = ""
    normalized["H4_Transition_Time"] = normalized["H4_Transition_Time"].fillna("").astype(str)
    return normalized.reindex(columns=TRANSITION_ALIGNMENT_COLUMNS)


def _normalize_h4_ohlc(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=H4_OHLC_COLUMNS + ["Timestamp"])
    normalized = frame.copy()
    for column in H4_OHLC_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = 0 if column != "Date" else ""
    normalized["Timestamp"] = pd.to_datetime(normalized["Date"], errors="coerce")
    for column in ["Open", "High", "Low", "Close", "Volume"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    normalized = normalized.dropna(subset=["Timestamp", "Open", "High", "Low", "Close"]).copy()
    return normalized.sort_values("Timestamp").reset_index(drop=True)
