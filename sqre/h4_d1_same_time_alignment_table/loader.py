"""Load timestamped H4/D1 inputs for same-time alignment."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def expected_input_paths(timestamped_state_regime_dir: Path, synchronized_data_dir: Path) -> dict[str, Path]:
    return {
        "timestamped_h4_market_states": timestamped_state_regime_dir / "timestamped_h4_market_states.csv",
        "timestamped_h4_state_transitions": timestamped_state_regime_dir / "timestamped_h4_state_transitions.csv",
        "timestamped_d1_market_states": timestamped_state_regime_dir / "timestamped_d1_market_states.csv",
        "timestamped_h4_d1_state_regime_summary": timestamped_state_regime_dir
        / "timestamped_h4_d1_state_regime_summary.csv",
        "h4_d1_candle_alignment_map": synchronized_data_dir / "h4_d1_candle_alignment_map.csv",
    }


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(resolved)
    except (EmptyDataError, ParserError):
        return pd.DataFrame()


def load_h4_transitions(timestamped_state_regime_dir: Path) -> pd.DataFrame:
    frame = read_optional_csv(timestamped_state_regime_dir / "timestamped_h4_state_transitions.csv")
    return _with_datetime_columns(frame, ["Transition_Time"])


def load_h4_states(timestamped_state_regime_dir: Path) -> pd.DataFrame:
    frame = read_optional_csv(timestamped_state_regime_dir / "timestamped_h4_market_states.csv")
    return _with_datetime_columns(frame, ["State_Event_Time", "State_Start_Time", "State_End_Time"])


def load_d1_states(timestamped_state_regime_dir: Path) -> pd.DataFrame:
    frame = read_optional_csv(timestamped_state_regime_dir / "timestamped_d1_market_states.csv")
    return _with_datetime_columns(frame, ["D1_Period_Start", "D1_Period_End"])


def load_candle_alignment_map(synchronized_data_dir: Path) -> pd.DataFrame:
    frame = read_optional_csv(synchronized_data_dir / "h4_d1_candle_alignment_map.csv")
    return _with_datetime_columns(frame, ["H4_Timestamp", "D1_Period_Start", "D1_Period_End"])


def _with_datetime_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if frame.empty:
        return frame
    normalized = frame.copy()
    for column in columns:
        if column in normalized.columns:
            normalized[column] = pd.to_datetime(normalized[column], errors="coerce")
    return normalized
