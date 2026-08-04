import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_cli_runs_with_synthetic_inputs(tmp_path):
    reference_dir = tmp_path / "reference"
    alignment_dir = tmp_path / "alignment"
    output_dir = tmp_path / "output"
    reference_dir.mkdir()
    alignment_dir.mkdir()
    _write_reference_store(reference_dir)
    _write_alignment(alignment_dir)

    command = [
        sys.executable,
        "scripts/run_research_reference_store_usage_review.py",
        "--reference-store-dir",
        str(reference_dir),
        "--interpretation-dir",
        str(tmp_path / "missing_interpretation"),
        "--same-time-alignment-dir",
        str(alignment_dir),
        "--output-dir",
        str(output_dir),
        "--report",
        str(output_dir / "report.txt"),
        "--preferred-horizons",
        "1",
    ]

    completed = subprocess.run(command, cwd=Path(__file__).resolve().parents[1], check=True, capture_output=True, text=True)

    assert "Research reference store usage review completed" in completed.stdout
    assert (output_dir / "research_reference_store_usage_review_summary.csv").exists()


def _write_reference_store(path):
    pd.DataFrame(
        [
            {
                "Research_Reference_ID": "REF_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "Outcome_Profile_ID": "OUT_1",
                "Context_Granularity": "D1_STATE_REGIME",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 1,
                "Outcome_Sample_Size": 25,
                "Outcome_Dispersion_Pips": 30.0,
                "Reference_Tier": "CORE_REFERENCE",
            }
        ]
    ).to_csv(path / "research_reference_store.csv", index=False)


def _write_alignment(path):
    pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
            }
        ]
    ).to_csv(path / "h4_transition_d1_same_time_alignment.csv", index=False)
