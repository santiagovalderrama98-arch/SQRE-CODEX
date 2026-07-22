from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_feasibility_inputs(tmp_path: Path, *, raw_file: Path | None = None) -> Path:
    feasibility_dir = tmp_path / "feasibility"
    feasibility_dir.mkdir()
    pd.DataFrame(
        [
            {
                "scenario_id": "eurusd_h4_period_5_partial",
                "symbol": "EURUSD",
                "timeframe": "H4",
                "defined_start_date": "2024-01-01",
                "defined_end_date": "2024-06-30",
                "coverage_ratio": 0.62,
                "raw_file_path": str(raw_file or ""),
                "feasibility_class": "FEASIBLE_PARTIAL_SAMPLE",
            },
            {
                "scenario_id": "eurusd_h4_period_6",
                "symbol": "EURUSD",
                "timeframe": "H4",
                "coverage_ratio": 1.0,
                "feasibility_class": "ALREADY_VALIDATED",
            },
        ]
    ).to_csv(feasibility_dir / "h4_feasible_expansion_candidates.csv", index=False)
    pd.DataFrame(
        [
            {
                "scenario_id": "eurusd_h4_period_5_partial",
                "actual_start_date": "2024-01-10",
                "actual_end_date": "2024-05-20",
                "raw_file_path": str(raw_file or ""),
            }
        ]
    ).to_csv(feasibility_dir / "h4_availability_review.csv", index=False)
    return feasibility_dir


def write_raw_ohlc(path: Path, rows: int = 30) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = []
    for index in range(rows):
        data.append(
            {
                "Date": f"2024-01-{1 + index // 6:02d} {4 * (index % 6):02d}:00:00",
                "Open": 1.1000 + index * 0.0001,
                "High": 1.1010 + index * 0.0001,
                "Low": 1.0990 + index * 0.0001,
                "Close": 1.1005 + index * 0.0001,
                "Volume": 0,
            }
        )
    pd.DataFrame(data).to_csv(path, index=False)
    return path


def write_baseline_inputs(tmp_path: Path) -> tuple[Path, Path]:
    validation_dir = tmp_path / "baseline_validation"
    research_dir = tmp_path / "baseline_research"
    validation_dir.mkdir()
    research_dir.mkdir()
    pd.DataFrame(
        [
            {"Scenario_ID": "eurusd_h4_period_1", "Timeframe": "H4", "OHLC_Rows": 1000, "Structure_Count": 50, "State_Count": 50, "Transition_Count": 49},
            {"Scenario_ID": "eurusd_h4_period_2", "Timeframe": "H4", "OHLC_Rows": 900, "Structure_Count": 40, "State_Count": 40, "Transition_Count": 39},
        ]
    ).to_csv(validation_dir / "h4_d1_validation_summary.csv", index=False)
    pd.DataFrame(
        [
            {"Timeframe": "H4", "Average_Forward_Range_Pips": 12.0, "Average_Outcome_Magnitude_Pips": 8.0},
            {"Timeframe": "H4", "Average_Forward_Range_Pips": 10.0, "Average_Outcome_Magnitude_Pips": 6.0},
        ]
    ).to_csv(research_dir / "h4_d1_price_outcome_profiles.csv", index=False)
    return validation_dir, research_dir
