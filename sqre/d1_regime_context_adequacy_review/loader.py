"""Load D1 regime context adequacy review inputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def expected_input_paths(
    contextual_transition_dir: Path,
    same_time_alignment_dir: Path,
    timestamped_state_regime_dir: Path,
) -> dict[str, Path]:
    return {
        "h4_d1_same_time_contextual_transition_profiles": contextual_transition_dir
        / "h4_d1_same_time_contextual_transition_profiles.csv",
        "h4_transition_d1_market_state_distribution": contextual_transition_dir
        / "h4_transition_d1_market_state_distribution.csv",
        "h4_transition_d1_regime_distribution": contextual_transition_dir
        / "h4_transition_d1_regime_distribution.csv",
        "h4_transition_context_concentration_review": contextual_transition_dir
        / "h4_transition_context_concentration_review.csv",
        "h4_d1_context_sample_adequacy_review": contextual_transition_dir
        / "h4_d1_context_sample_adequacy_review.csv",
        "h4_d1_same_time_contextual_transition_review_summary": contextual_transition_dir
        / "h4_d1_same_time_contextual_transition_review_summary.csv",
        "h4_transition_d1_same_time_alignment": same_time_alignment_dir
        / "h4_transition_d1_same_time_alignment.csv",
        "h4_state_d1_same_time_alignment": same_time_alignment_dir / "h4_state_d1_same_time_alignment.csv",
        "h4_d1_same_time_alignment_summary": same_time_alignment_dir / "h4_d1_same_time_alignment_summary.csv",
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


def load_profiles(contextual_transition_dir: Path) -> pd.DataFrame:
    frame = read_optional_csv(contextual_transition_dir / "h4_d1_same_time_contextual_transition_profiles.csv")
    return _normalize_profiles(frame)


def load_market_state_distribution(contextual_transition_dir: Path) -> pd.DataFrame:
    return read_optional_csv(contextual_transition_dir / "h4_transition_d1_market_state_distribution.csv")


def load_regime_distribution(contextual_transition_dir: Path) -> pd.DataFrame:
    return read_optional_csv(contextual_transition_dir / "h4_transition_d1_regime_distribution.csv")


def load_concentration_review(contextual_transition_dir: Path) -> pd.DataFrame:
    return read_optional_csv(contextual_transition_dir / "h4_transition_context_concentration_review.csv")


def load_contextual_sample_review(contextual_transition_dir: Path) -> pd.DataFrame:
    return read_optional_csv(contextual_transition_dir / "h4_d1_context_sample_adequacy_review.csv")


def load_contextual_summary(contextual_transition_dir: Path) -> pd.DataFrame:
    return read_optional_csv(contextual_transition_dir / "h4_d1_same_time_contextual_transition_review_summary.csv")


def _normalize_profiles(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    normalized = frame.copy()
    defaults = {
        "Context_Profile_ID": "",
        "H4_Transition_Label": "",
        "D1_Market_State": "",
        "D1_Regime_Label": "",
        "D1_Structure_Direction": "",
        "Context_Row_Count": 0,
        "Transition_Total_Count": 0,
        "Context_Sample_Adequacy_Class": "",
        "Contextual_Review_Class": "",
    }
    for column, default in defaults.items():
        if column not in normalized.columns:
            normalized[column] = default
    for column in ["Context_Row_Count", "Transition_Total_Count"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce").fillna(0).astype(int)
    for column in [
        "Context_Profile_ID",
        "H4_Transition_Label",
        "D1_Market_State",
        "D1_Regime_Label",
        "D1_Structure_Direction",
        "Context_Sample_Adequacy_Class",
        "Contextual_Review_Class",
    ]:
        normalized[column] = normalized[column].fillna("").astype(str)
    return normalized
