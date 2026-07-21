import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.availability_review import (
    build_availability_review,
    classify_availability_status,
)
from sqre.h4_expanded_sample_feasibility_review.config import H4ExpandedSampleFeasibilityConfig
from sqre.h4_expanded_sample_feasibility_review.models import DefinedSampleRow, RawFileInventoryRow


def test_classify_availability_status_uses_thresholds():
    config = H4ExpandedSampleFeasibilityConfig(minimum_full_coverage_ratio=0.9, minimum_partial_coverage_ratio=0.5)

    assert classify_availability_status("", 0.95, None, config) == "AVAILABLE_FULL"
    assert classify_availability_status("", 0.50, None, config) == "AVAILABLE_PARTIAL"
    assert classify_availability_status("missing", 0.00, None, config) == "MISSING"


def test_build_availability_review_combines_definition_availability_and_raw():
    definition = DefinedSampleRow(
        "eurusd_h4_period_1",
        "EURUSD",
        "H4",
        "2020-01-01",
        "2020-01-31",
        "samples.yaml",
        "DEFINED",
        "",
        "data/raw/EURUSD_H4_period_1.csv",
    )
    raw = RawFileInventoryRow(
        "data/raw/EURUSD_H4_period_1.csv",
        "EURUSD_H4_period_1.csv",
        "NO",
        "EURUSD",
        "H4",
        100,
        "2020-01-01",
        "2020-01-31",
        "KNOWN",
        "",
    )
    availability = pd.DataFrame(
        [{"Scenario_ID": "eurusd_h4_period_1", "Timeframe": "H4", "Coverage_Ratio": 0.75}]
    )

    rows = build_availability_review([definition], availability, [raw], H4ExpandedSampleFeasibilityConfig())

    assert len(rows) == 1
    assert rows[0].availability_status == "AVAILABLE_PARTIAL"
    assert rows[0].coverage_ratio == 0.75
    assert rows[0].raw_file_path == "data/raw/EURUSD_H4_period_1.csv"
