from pathlib import Path

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.h4_d1_synchronized_data_pipeline import (
    run_h4_d1_synchronized_data_preparation,
)
from sqre.h4_d1_synchronized_data_preparation.reports import FORBIDDEN_REPORT_TERMS, build_report_text


def test_report_contains_scope_sections_without_forbidden_terms(tmp_path: Path):
    h4_input = tmp_path / "EURUSD_H4.csv"
    pd.DataFrame(
        {
            "Date": [
                "2026-07-01 00:00:00",
                "2026-07-01 04:00:00",
                "2026-07-01 08:00:00",
                "2026-07-01 12:00:00",
                "2026-07-01 16:00:00",
                "2026-07-01 20:00:00",
            ],
            "Open": [1, 2, 3, 4, 5, 6],
            "High": [2, 3, 4, 5, 6, 7],
            "Low": [0, 1, 2, 3, 4, 5],
            "Close": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
            "Volume": [1, 1, 1, 1, 1, 1],
        }
    ).to_csv(h4_input, index=False)
    result = run_h4_d1_synchronized_data_preparation(
        H4D1SynchronizedDataPreparationConfig(
            h4_input=h4_input,
            output_dir=tmp_path / "out",
            report_path=tmp_path / "out" / "report.txt",
        )
    )

    report = build_report_text(result)
    lowered = report.lower()

    assert "SQRE H4/D1 Synchronized Historical Data Preparation" in report
    assert "This phase prepares synchronized H4/D1 OHLC data only." in report
    assert "does not generate market states" in report
    assert "does not generate D1 regimes" in report
    assert all(term not in lowered for term in FORBIDDEN_REPORT_TERMS)
