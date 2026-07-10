from __future__ import annotations

import subprocess
import sys

import pandas as pd


def _write_structures(path) -> None:
    pd.DataFrame(
        {
            "Structure_ID": ["STR_000001"],
            "Symbol": ["EURUSD"],
            "Timeframe": ["H4"],
            "Start_Time": ["2026-01-01 00:00:00"],
            "End_Time": ["2026-01-01 04:00:00"],
            "Direction": ["UP"],
            "Lifecycle_Stage": ["DEVELOPMENT"],
            "Persistence_Index": [0.10],
            "Structural_Complexity": [0.10],
            "Structural_Stability": [0.70],
            "Structural_Efficiency": [0.62],
            "Event_Density": [0.20],
            "Structural_Volatility": [0.20],
            "Structural_Symmetry": [0.70],
            "Structural_Confidence": [0.58],
            "Duration_Seconds": [14400],
            "Price_Displacement": [0.0010],
            "Event_Count": [8],
            "Leg_Count": [4],
        }
    ).to_csv(path, index=False)


def test_run_market_states_cli_preserves_default_behavior(tmp_path) -> None:
    structures = tmp_path / "structures.csv"
    output = tmp_path / "market_states.csv"
    report = tmp_path / "market_states_report.txt"
    _write_structures(structures)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_market_states.py",
            "--structures",
            str(structures),
            "--output",
            str(output),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    frame = pd.read_csv(output)
    assert frame.loc[0, "Market_State"] == "DIRECTIONAL_DISPLACEMENT"


def test_run_market_states_cli_accepts_profile_and_timeframe(tmp_path) -> None:
    structures = tmp_path / "structures.csv"
    output = tmp_path / "market_states.csv"
    report = tmp_path / "market_states_report.txt"
    _write_structures(structures)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_market_states.py",
            "--structures",
            str(structures),
            "--output",
            str(output),
            "--report",
            str(report),
            "--state-config",
            "configs/validation/state_threshold_profiles.yaml",
            "--state-profile",
            "directional_stricter",
            "--timeframe",
            "H4",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    frame = pd.read_csv(output)
    assert frame.loc[0, "Market_State"] == "UNCLASSIFIED"
