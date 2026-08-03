from pathlib import Path

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.h4_d1_synchronized_data_pipeline import (
    run_h4_d1_synchronized_data_preparation,
)


def test_pipeline_writes_expected_outputs_for_synthetic_h4_data(tmp_path: Path):
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
    output_dir = tmp_path / "out"

    result = run_h4_d1_synchronized_data_preparation(
        H4D1SynchronizedDataPreparationConfig(
            h4_input=h4_input,
            output_dir=output_dir,
            report_path=output_dir / "h4_d1_synchronized_data_report.txt",
        )
    )

    assert result.summary is not None
    assert result.summary.h4_row_count == 6
    assert result.summary.d1_row_count == 1
    assert result.summary.h4_d1_synchronized_data_readiness_flag == "READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION"
    assert (output_dir / "h4_normalized_ohlc.csv").exists()
    assert (output_dir / "d1_from_h4_ohlc.csv").exists()
    assert (output_dir / "h4_d1_candle_alignment_map.csv").exists()
    assert (output_dir / "h4_d1_synchronized_data_summary.csv").exists()
