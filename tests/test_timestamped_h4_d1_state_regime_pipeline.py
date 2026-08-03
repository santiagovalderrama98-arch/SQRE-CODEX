from pathlib import Path

import pandas as pd

from sqre.timestamped_h4_d1_state_regime_generation.config import TimestampedH4D1StateRegimeGenerationConfig
from sqre.timestamped_h4_d1_state_regime_generation.timestamped_h4_d1_state_regime_pipeline import (
    run_timestamped_h4_d1_state_regime_generation,
)
from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_pipeline_writes_all_expected_outputs(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync")
    output_dir = tmp_path / "out"

    result = run_timestamped_h4_d1_state_regime_generation(
        TimestampedH4D1StateRegimeGenerationConfig(
            synchronized_data_dir=input_dir,
            output_dir=output_dir,
            report_path=output_dir / "timestamped_h4_d1_state_regime_report.txt",
        )
    )

    expected = [
        "timestamped_h4_d1_source_inventory.csv",
        "timestamped_h4_market_states.csv",
        "timestamped_h4_state_transitions.csv",
        "timestamped_d1_market_states.csv",
        "timestamped_h4_d1_generation_coverage_review.csv",
        "timestamped_h4_d1_missing_output_review.csv",
        "timestamped_h4_d1_state_regime_summary.csv",
        "timestamped_h4_d1_state_regime_report.txt",
    ]
    for filename in expected:
        assert (output_dir / filename).exists()
    assert result.summary is not None
    assert result.summary.timestamped_h4_d1_state_regime_readiness_flag == "READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE"


def test_pipeline_writes_empty_outputs_for_missing_input(tmp_path: Path):
    output_dir = tmp_path / "out"

    result = run_timestamped_h4_d1_state_regime_generation(
        TimestampedH4D1StateRegimeGenerationConfig(
            synchronized_data_dir=tmp_path / "missing_sync",
            output_dir=output_dir,
            report_path=output_dir / "report.txt",
        )
    )

    summary = pd.read_csv(output_dir / "timestamped_h4_d1_state_regime_summary.csv")
    assert result.h4_states.empty
    assert summary["Timestamped_H4_D1_State_Regime_Readiness_Flag"].iloc[0] == "INPUT_COMPLETENESS_REVIEW_REQUIRED"
