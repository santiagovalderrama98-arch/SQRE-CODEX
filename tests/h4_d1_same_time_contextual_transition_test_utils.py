from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_transition_alignment(path: Path) -> pd.DataFrame:
    path.mkdir(parents=True, exist_ok=True)
    rows = []
    for index in range(18):
        rows.append(
            {
                "H4_D1_Transition_Alignment_ID": f"A{index}",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_ID": f"T{index}",
                "H4_Transition_Time": "2026-01-01 00:00:00",
                "H4_Transition_Date": "2026-01-01",
                "H4_Source_State": "RANGE_CONTRACTION",
                "H4_Target_State": "DIRECTIONAL_DISPLACEMENT",
                "H4_Transition_Label": "RANGE_CONTRACTION -> DIRECTIONAL_DISPLACEMENT",
                "D1_State_ID": "D1A",
                "D1_Date": "2026-01-01",
                "D1_Period_Start": "2026-01-01 00:00:00",
                "D1_Period_End": "2026-01-01 23:59:59",
                "D1_Market_State": "D1_TREND",
                "D1_Regime_Label": "D1_EXPANSION",
                "D1_Structure_Direction": "UP",
                "Alignment_Method": "D1_INTERVAL_CONTAINMENT_MATCH",
                "Alignment_Confidence_Class": "HIGH_CONFIDENCE_SAME_TIME_ALIGNMENT",
                "Alignment_Diagnostic": "Matched.",
            }
        )
    for index in range(6):
        rows.append(
            {
                "H4_D1_Transition_Alignment_ID": f"B{index}",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_ID": f"U{index}",
                "H4_Transition_Time": "2026-01-02 00:00:00",
                "H4_Transition_Date": "2026-01-02",
                "H4_Source_State": "DIRECTIONAL_DISPLACEMENT",
                "H4_Target_State": "RANGE_CONTRACTION",
                "H4_Transition_Label": "DIRECTIONAL_DISPLACEMENT -> RANGE_CONTRACTION",
                "D1_State_ID": "D1B",
                "D1_Date": "2026-01-02",
                "D1_Period_Start": "2026-01-02 00:00:00",
                "D1_Period_End": "2026-01-02 23:59:59",
                "D1_Market_State": "D1_RANGE",
                "D1_Regime_Label": "D1_CONSOLIDATION",
                "D1_Structure_Direction": "DOWN",
                "Alignment_Method": "D1_DATE_MATCH",
                "Alignment_Confidence_Class": "MODERATE_CONFIDENCE_SAME_TIME_ALIGNMENT",
                "Alignment_Diagnostic": "Matched.",
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(path / "h4_transition_d1_same_time_alignment.csv", index=False)
    pd.DataFrame({"Any": [1]}).to_csv(path / "h4_state_d1_same_time_alignment.csv", index=False)
    pd.DataFrame({"Any": [1]}).to_csv(path / "h4_d1_same_time_alignment_coverage_review.csv", index=False)
    pd.DataFrame({"Any": [1]}).to_csv(path / "h4_d1_same_time_alignment_summary.csv", index=False)
    return frame
