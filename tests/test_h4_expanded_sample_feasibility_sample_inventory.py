from pathlib import Path

from sqre.h4_expanded_sample_feasibility_review.sample_inventory import (
    extract_h4_samples_from_config,
    merge_defined_samples,
)


def test_extract_h4_samples_from_config_filters_non_h4():
    rows = extract_h4_samples_from_config(
        {
            "samples": [
                {
                    "sample_id": "eurusd_h4_period_1",
                    "symbol": "EURUSD",
                    "timeframe": "H4",
                    "start": "2020-01-01",
                    "end": "2020-02-01",
                    "output_path": "data/raw/EURUSD_H4_period_1.csv",
                },
                {"sample_id": "eurusd_d1_period_1", "timeframe": "D1"},
            ]
        },
        Path("samples.yaml"),
    )

    assert len(rows) == 1
    assert rows[0].scenario_id == "eurusd_h4_period_1"
    assert rows[0].sample_definition_status == "DEFINED"


def test_merge_defined_samples_prefers_more_complete_row():
    incomplete = extract_h4_samples_from_config(
        {"scenarios": [{"scenario_id": "eurusd_h4_period_1", "timeframe": "H4"}]},
        "a.yaml",
    )
    complete = extract_h4_samples_from_config(
        {
            "scenarios": [
                {
                    "scenario_id": "eurusd_h4_period_1",
                    "timeframe": "H4",
                    "start_date": "2020-01-01",
                    "end_date": "2020-01-31",
                }
            ]
        },
        "b.yaml",
    )

    merged = merge_defined_samples([incomplete, complete])

    assert len(merged) == 1
    assert merged[0].source_config == "b.yaml"
    assert merged[0].defined_start_date == "2020-01-01"
