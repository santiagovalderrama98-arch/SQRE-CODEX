import subprocess
import sys

import pandas as pd


def test_cli_runs_user_supplied_snapshot(tmp_path):
    ref = tmp_path / "reference"
    query = tmp_path / "query"
    out = tmp_path / "out"
    ref.mkdir()
    query.mkdir()
    pd.DataFrame([_reference()]).to_csv(ref / "research_reference_store.csv", index=False)
    pd.DataFrame([{"Research_Query_ID": "RQ_1"}]).to_csv(query / "research_query_requests.csv", index=False)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_current_market_state_snapshot_research.py",
            "--reference-store-dir",
            str(ref),
            "--query-interface-dir",
            str(query),
            "--usage-review-dir",
            str(tmp_path / "usage"),
            "--same-time-alignment-dir",
            str(tmp_path / "alignment"),
            "--timestamped-state-regime-dir",
            str(tmp_path / "timestamped"),
            "--output-dir",
            str(out),
            "--report",
            str(out / "report.txt"),
            "--snapshot-mode",
            "USER_SUPPLIED_SNAPSHOT",
            "--snapshot-h4-transition-label",
            "A_TO_B",
            "--snapshot-d1-market-state",
            "STATE",
            "--snapshot-d1-regime-label",
            "REGIME",
            "--snapshot-forward-horizon",
            "1",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Current market state snapshot research completed" in completed.stdout
    assert (out / "current_market_state_snapshot_research_summary.csv").exists()


def _reference() -> dict[str, object]:
    return {
        "Research_Reference_ID": "RRS_1",
        "Outcome_Profile_ID": "OP_1",
        "Context_Granularity": "EXACT",
        "Reference_Tier": "CORE_REFERENCE",
        "H4_Transition_Label": "A_TO_B",
        "D1_Market_State": "STATE",
        "D1_Regime_Label": "REGIME",
        "Forward_Horizon_H4_Candles": 1,
        "Outcome_Sample_Size": 30,
        "Outcome_Dispersion_Pips": 20,
    }
