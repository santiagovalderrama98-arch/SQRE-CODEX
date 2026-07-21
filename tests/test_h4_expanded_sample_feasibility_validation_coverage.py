from pathlib import Path

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.models import AvailabilityReviewRow
from sqre.h4_expanded_sample_feasibility_review.validation_coverage_review import build_validation_coverage_review


def test_build_validation_coverage_review_marks_validated_scenario(tmp_path: Path):
    availability = [
        AvailabilityReviewRow(
            "eurusd_h4_period_1",
            "EURUSD",
            "H4",
            "2020-01-01",
            "2020-01-31",
            "AVAILABLE_FULL",
            1.0,
            "2020-01-01",
            "2020-01-31",
            "data/raw/EURUSD_H4_period_1.csv",
            "NO",
            "",
        )
    ]
    evidence = pd.DataFrame(
        [
            {
                "Scenario_ID": "eurusd_h4_period_1",
                "Timeframe": "H4",
                "OHLC_Rows": 100,
                "Structure_Count": 10,
                "State_Count": 9,
                "Transition_Count": 8,
            }
        ]
    )

    rows = build_validation_coverage_review(availability, [evidence], tmp_path)

    assert rows[0].validation_status == "VALIDATED"
    assert rows[0].ohlc_rows == 100
    assert rows[0].transition_count == 8


def test_build_validation_coverage_review_marks_available_not_validated(tmp_path: Path):
    availability = [
        AvailabilityReviewRow("eurusd_h4_period_2", "EURUSD", "H4", "", "", "AVAILABLE_PARTIAL", 0.5, "", "", "", "NO", "")
    ]

    rows = build_validation_coverage_review(availability, [pd.DataFrame()], tmp_path)

    assert rows[0].validation_status == "NOT_VALIDATED"
    assert rows[0].research_output_status == "MISSING"
