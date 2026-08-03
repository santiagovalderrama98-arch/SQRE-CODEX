"""Load H4/D1 same-time contextual transition review inputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def expected_input_paths(same_time_alignment_dir: Path, timestamped_state_regime_dir: Path) -> dict[str, Path]:
    return {
        "h4_transition_d1_same_time_alignment": same_time_alignment_dir
        / "h4_transition_d1_same_time_alignment.csv",
        "h4_state_d1_same_time_alignment": same_time_alignment_dir / "h4_state_d1_same_time_alignment.csv",
        "h4_d1_same_time_alignment_coverage_review": same_time_alignment_dir
        / "h4_d1_same_time_alignment_coverage_review.csv",
        "h4_d1_same_time_alignment_summary": same_time_alignment_dir / "h4_d1_same_time_alignment_summary.csv",
        "timestamped_h4_market_states": timestamped_state_regime_dir / "timestamped_h4_market_states.csv",
        "timestamped_h4_state_transitions": timestamped_state_regime_dir / "timestamped_h4_state_transitions.csv",
        "timestamped_d1_market_states": timestamped_state_regime_dir / "timestamped_d1_market_states.csv",
        "timestamped_h4_d1_state_regime_summary": timestamped_state_regime_dir
        / "timestamped_h4_d1_state_regime_summary.csv",
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


def load_state_alignment(same_time_alignment_dir: Path) -> pd.DataFrame:
    return read_optional_csv(same_time_alignment_dir / "h4_state_d1_same_time_alignment.csv")


def load_coverage_review(same_time_alignment_dir: Path) -> pd.DataFrame:
    return read_optional_csv(same_time_alignment_dir / "h4_d1_same_time_alignment_coverage_review.csv")


def load_alignment_summary(same_time_alignment_dir: Path) -> pd.DataFrame:
    return read_optional_csv(same_time_alignment_dir / "h4_d1_same_time_alignment_summary.csv")


def _normalize_transition_alignment(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    normalized = frame.copy()
    for column in ["H4_Transition_Label", "D1_Market_State", "D1_Regime_Label", "D1_Structure_Direction"]:
        if column not in normalized.columns:
            normalized[column] = ""
        normalized[column] = normalized[column].fillna("").astype(str)
    if "Alignment_Method" not in normalized.columns:
        normalized["Alignment_Method"] = ""
    return normalized
