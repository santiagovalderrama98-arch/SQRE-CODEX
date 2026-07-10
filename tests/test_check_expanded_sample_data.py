import importlib.util
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_check_samples_reports_available_missing_and_invalid_files(tmp_path):
    module = _load_module()
    valid_path = tmp_path / "valid.csv"
    invalid_path = tmp_path / "invalid.csv"
    missing_path = tmp_path / "missing.csv"
    pd.DataFrame(
        [
            {
                "Date": "2026-01-01 00:00:00",
                "Open": 1.1,
                "High": 1.2,
                "Low": 1.0,
                "Close": 1.15,
                "Volume": 0,
            }
        ]
    ).to_csv(valid_path, index=False)
    pd.DataFrame([{"Date": "2026-01-01 00:00:00", "Open": 1.1}]).to_csv(invalid_path, index=False)
    config = {
        "sample_set_name": "sample_set",
        "samples": [
            _sample("available", "M5", valid_path),
            _sample("invalid", "H1", invalid_path),
            _sample("missing", "H4", missing_path),
        ],
    }

    results = module.check_samples(config, {"available", "invalid", "missing"})

    by_id = {result.sample_id: result for result in results}
    assert by_id["available"].status == "AVAILABLE"
    assert by_id["available"].rows == 1
    assert by_id["available"].valid_columns is True
    assert by_id["invalid"].status == "INVALID_COLUMNS"
    assert by_id["missing"].status == "MISSING"


def test_check_sample_outputs_csv_and_report(tmp_path):
    module = _load_module()
    results = [
        module.AvailabilityResult(
            sample_id="available",
            scenario_id="available",
            symbol="EURUSD",
            timeframe="M5",
            expected_start="2026-01-01",
            expected_end="2026-01-02",
            output_path="data/raw/EURUSD_M5_period_3.csv",
            exists=True,
            rows=10,
            valid_columns=True,
            first_date="2026-01-01 00:00:00",
            last_date="2026-01-02 00:00:00",
            status="AVAILABLE",
            message="ok",
        ),
        module.AvailabilityResult(
            sample_id="missing",
            scenario_id="missing",
            symbol="EURUSD",
            timeframe="H1",
            expected_start="2026-01-01",
            expected_end="2026-01-02",
            output_path="data/raw/EURUSD_H1_period_2.csv",
            exists=False,
            rows=0,
            valid_columns=False,
            first_date="",
            last_date="",
            status="MISSING",
            message="File not found",
        ),
    ]

    csv_path = module.write_availability_csv(tmp_path / "availability.csv", results)
    report_path = module.write_availability_report(
        tmp_path / "availability.txt",
        {"sample_set_name": "sample_set"},
        {"available", "missing"},
        results,
    )

    frame = pd.read_csv(csv_path)
    report = report_path.read_text(encoding="utf-8")
    assert list(frame["Status"]) == ["AVAILABLE", "MISSING"]
    assert "SQRE Expanded Historical Data Availability Report" in report
    assert "Total Samples: 2" in report
    assert "Missing: 1" in report
    assert "- H1: total=1, available=0, missing=1" in report


def test_load_validation_scenario_ids_reads_scenario_ids(tmp_path):
    module = _load_module()
    path = tmp_path / "validation.yaml"
    path.write_text(
        """
validation_name: sample
scenarios:
  - scenario_id: eurusd_m5_period_3
  - scenario_id: eurusd_h1_period_2
""",
        encoding="utf-8",
    )

    assert module.load_validation_scenario_ids(path) == {"eurusd_m5_period_3", "eurusd_h1_period_2"}


def _sample(sample_id: str, timeframe: str, output_path: Path) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "symbol": "EURUSD",
        "timeframe": timeframe,
        "start": "2026-01-01",
        "end": "2026-01-02",
        "output_path": str(output_path),
    }


def _load_module():
    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    path = scripts_dir / "check_expanded_sample_data.py"
    spec = importlib.util.spec_from_file_location("check_expanded_sample_data", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
