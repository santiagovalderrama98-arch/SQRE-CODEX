from pathlib import Path

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.config import H4ExpandedSampleFeasibilityConfig
from sqre.h4_expanded_sample_feasibility_review.h4_expanded_sample_feasibility_review_pipeline import (
    run_h4_expanded_sample_feasibility_review,
)


def write_pipeline_inputs(tmp_path: Path) -> H4ExpandedSampleFeasibilityConfig:
    config_dir = tmp_path / "configs"
    validation_dir = tmp_path / "validation"
    research_dir = tmp_path / "research"
    raw_dir = tmp_path / "raw"
    partial_dir = raw_dir / "partial"
    for directory in [config_dir, validation_dir, research_dir, raw_dir, partial_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    sample_config = config_dir / "samples.yaml"
    sample_config.write_text(
        """
samples:
  - sample_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
    start: 2020-01-01
    end: 2020-01-31
    output_path: raw/EURUSD_H4_period_1.csv
""",
        encoding="utf-8",
    )
    expanded_config = config_dir / "expanded.yaml"
    expanded_config.write_text(
        """
scenarios:
  - scenario_id: eurusd_h4_period_2
    symbol: EURUSD
    timeframe: H4
    start_date: 2020-02-01
    end_date: 2020-02-29
    ohlc_path: raw/partial/EURUSD_H4_period_2.csv
""",
        encoding="utf-8",
    )
    h4_d1_config = config_dir / "h4d1.yaml"
    h4_d1_config.write_text("scenarios: []\n", encoding="utf-8")
    availability_csv = validation_dir / "availability.csv"
    availability_csv.write_text(
        "Scenario_ID,Timeframe,Coverage_Ratio\n"
        "eurusd_h4_period_1,H4,1.0\n"
        "eurusd_h4_period_2,H4,0.5\n",
        encoding="utf-8",
    )
    h4_d1_summary = validation_dir / "h4_d1_validation_summary.csv"
    h4_d1_summary.write_text(
        "Scenario_ID,Timeframe,OHLC_Rows,Structure_Count,State_Count,Transition_Count\n"
        "eurusd_h4_period_1,H4,100,10,9,8\n",
        encoding="utf-8",
    )
    for path in [validation_dir / "master.csv", validation_dir / "expanded_summary.csv"]:
        path.write_text("Scenario_ID,Timeframe\n", encoding="utf-8")
    research_dir.joinpath("h4_d1_timeframe_research_summary.csv").write_text("Scenario_ID,Timeframe\n", encoding="utf-8")
    research_dir.joinpath("h4_d1_scenario_inventory.csv").write_text("Scenario_ID,Timeframe\n", encoding="utf-8")
    raw_dir.joinpath("EURUSD_H4_period_1.csv").write_text("Date\n2020-01-01\n2020-01-31\n", encoding="utf-8")
    partial_dir.joinpath("EURUSD_H4_period_2.csv").write_text("Date\n2020-02-01\n2020-02-15\n", encoding="utf-8")
    return H4ExpandedSampleFeasibilityConfig(
        sample_config=sample_config,
        expanded_validation_config=expanded_config,
        h4_d1_validation_config=h4_d1_config,
        availability_csv=availability_csv,
        master_summary_csv=validation_dir / "master.csv",
        expanded_summary_csv=validation_dir / "expanded_summary.csv",
        h4_d1_validation_summary=h4_d1_summary,
        h4_d1_research_dir=research_dir,
        raw_data_dir=raw_dir,
        partial_data_dir=partial_dir,
    )


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    config = write_pipeline_inputs(tmp_path)

    result = run_h4_expanded_sample_feasibility_review(tmp_path / "out", tmp_path / "out" / "report.txt", config)

    assert len(result.defined_samples) == 2
    assert len(result.raw_files) == 2
    assert len(result.availability_rows) == 2
    assert len(result.validation_rows) == 2
    assert len(result.feasibility_rows) == 2
    assert result.summary is not None
    assert result.summary.already_validated_count == 1
    assert result.summary.feasible_partial_sample_count == 1
    for name in [
        "h4_sample_source_inventory.csv",
        "h4_defined_sample_inventory.csv",
        "h4_raw_file_inventory.csv",
        "h4_availability_review.csv",
        "h4_validation_coverage_review.csv",
        "h4_expansion_feasibility_matrix.csv",
        "h4_feasible_expansion_candidates.csv",
        "h4_constrained_or_missing_samples.csv",
        "h4_expanded_sample_feasibility_summary.csv",
    ]:
        assert (result.output_dir / name).exists()
    matrix = pd.read_csv(result.output_dir / "h4_expansion_feasibility_matrix.csv")
    assert set(matrix["feasibility_class"]) == {"ALREADY_VALIDATED", "FEASIBLE_PARTIAL_SAMPLE"}
