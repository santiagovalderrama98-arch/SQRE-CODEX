import pandas as pd

from sqre.research_dashboard_prototype.evidence_panel_builder import build_evidence_panel


def test_evidence_panel_builder_summarizes_evidence_review():
    frames = {
        "snapshot_reference_results": pd.DataFrame(
            [
                {
                    "Snapshot_Query_ID": "Q1",
                    "Snapshot_Evidence_Class": "CORE_SNAPSHOT_REFERENCE_EVIDENCE",
                    "Matched_Outcome_Sample_Size": 10,
                    "Matched_Outcome_Dispersion_Pips": 8,
                },
                {
                    "Snapshot_Query_ID": "Q2",
                    "Snapshot_Evidence_Class": "SUPPORTING_SNAPSHOT_REFERENCE_EVIDENCE",
                    "Matched_Outcome_Sample_Size": 20,
                    "Matched_Outcome_Dispersion_Pips": 12,
                },
            ]
        )
    }

    panel = build_evidence_panel(frames)

    assert len(panel) == 2
    assert set(panel["Panel_Status"]) == {"PANEL_READY"}
