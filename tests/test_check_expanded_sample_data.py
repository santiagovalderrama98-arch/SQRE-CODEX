import importlib.util
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_check_samples_reports_available_missing_and_invalid_files(tmp_path):
    module = _load_module()
    valid_path = tmp_path / "valid.csv"
    invalid_path = tmp_path / "invalid.csv"
    missing_path = tmp_path / "missing.csv"
    _write_ohlc(valid_path, ["2026-01-01 00:00:00", "2026-01-02 00:00:00"])
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
    assert by_id["available"].status == "AVAILABLE_FULL"
    assert by_id["available"].coverage_status == "FULL"
    assert by_id["available"].rows == 2
    assert by_id["available"].valid_columns is True
    assert by_id["invalid"].status == "INVALID_COLUMNS"
    assert by_id["missing"].status == "MISSING"


def test_check_samples_reports_available_full_when_range_is_within_tolerance(tmp_path):
    module = _load_module()
    path = tmp_path / "h4_full.csv"
    _write_ohlc(path, ["2022-01-02 19:00:00", "2023-06-29 21:00:00"])
    config = {"sample_set_name": "sample_set", "samples": [_sample("h4_full", "H4", path, start="2022-01-01", end="2023-06-30")]}

    result = module.check_samples(config, {"h4_full"})[0]

    assert result.status == "AVAILABLE_FULL"
    assert result.coverage_status == "FULL"
    assert result.start_gap_days == 1
    assert result.end_gap_days == 1
    assert result.coverage_ratio >= 0.90


def test_check_samples_reports_available_partial_when_start_gap_is_too_large(tmp_path):
    module = _load_module()
    path = tmp_path / "h4_partial.csv"
    _write_ohlc(path, ["2020-01-30 04:00:00", "2020-06-29 21:00:00"])
    config = {"sample_set_name": "sample_set", "samples": [_sample("h4_partial", "H4", path, start="2019-01-01", end="2020-06-30")]}

    result = module.check_samples(config, {"h4_partial"})[0]

    assert result.status == "AVAILABLE_PARTIAL"
    assert result.coverage_status == "PARTIAL"
    assert result.start_gap_days > 7


def test_check_samples_reports_available_partial_when_end_gap_is_too_large(tmp_path):
    module = _load_module()
    path = tmp_path / "end_gap.csv"
    _write_ohlc(path, ["2026-01-01 00:00:00", "2026-01-20 00:00:00"])
    config = {"sample_set_name": "sample_set", "samples": [_sample("end_gap", "M5", path, start="2026-01-01", end="2026-01-31")]}

    result = module.check_samples(
        config,
        {"end_gap"},
        module.CoverageTolerances(min_coverage_ratio=0.10, max_start_gap_days=7, max_end_gap_days=7),
    )[0]

    assert result.status == "AVAILABLE_PARTIAL"
    assert result.coverage_status == "PARTIAL"
    assert result.end_gap_days == 11


def test_check_samples_reports_available_partial_when_coverage_ratio_is_low(tmp_path):
    module = _load_module()
    path = tmp_path / "low_ratio.csv"
    _write_ohlc(path, ["2026-01-01 00:00:00", "2026-01-15 00:00:00"])
    config = {"sample_set_name": "sample_set", "samples": [_sample("low_ratio", "M5", path, start="2026-01-01", end="2026-03-31")]}

    result = module.check_samples(
        config,
        {"low_ratio"},
        module.CoverageTolerances(min_coverage_ratio=0.90, max_start_gap_days=7, max_end_gap_days=100),
    )[0]

    assert result.status == "AVAILABLE_PARTIAL"
    assert result.coverage_status == "PARTIAL"
    assert result.coverage_ratio < 0.90


def test_check_samples_reports_empty_file_and_read_error(tmp_path):
    module = _load_module()
    empty_path = tmp_path / "empty.csv"
    read_error_path = tmp_path / "read_error"
    empty_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")
    read_error_path.mkdir()
    config = {
        "sample_set_name": "sample_set",
        "samples": [_sample("empty", "M5", empty_path), _sample("read_error", "H1", read_error_path)],
    }

    results = module.check_samples(config, {"empty", "read_error"})

    by_id = {result.sample_id: result for result in results}
    assert by_id["empty"].status == "EMPTY_FILE"
    assert by_id["empty"].coverage_status == "NOT_APPLICABLE"
    assert by_id["read_error"].status == "READ_ERROR"
    assert by_id["read_error"].coverage_status == "NOT_APPLICABLE"


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
            expected_duration_days=1,
            actual_coverage_days=1,
            start_gap_days=0,
            end_gap_days=0,
            coverage_ratio=1.0,
            coverage_status="FULL",
            status="AVAILABLE_FULL",
            message="ok",
        ),
        module.AvailabilityResult(
            sample_id="partial",
            scenario_id="partial",
            symbol="EURUSD",
            timeframe="H4",
            expected_start="2019-01-01",
            expected_end="2020-06-30",
            output_path="data/raw/EURUSD_H4_period_5.csv",
            exists=True,
            rows=674,
            valid_columns=True,
            first_date="2020-01-30 04:00:00",
            last_date="2020-06-29 21:00:00",
            expected_duration_days=546,
            actual_coverage_days=151,
            start_gap_days=394,
            end_gap_days=1,
            coverage_ratio=0.276557,
            coverage_status="PARTIAL",
            status="AVAILABLE_PARTIAL",
            message="partial",
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
            expected_duration_days="",
            actual_coverage_days="",
            start_gap_days="",
            end_gap_days="",
            coverage_ratio="",
            coverage_status="NOT_APPLICABLE",
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
    assert list(frame["Status"]) == ["AVAILABLE_FULL", "AVAILABLE_PARTIAL", "MISSING"]
    assert "Expected_Duration_Days" in frame.columns
    assert "Actual_Coverage_Days" in frame.columns
    assert "Start_Gap_Days" in frame.columns
    assert "End_Gap_Days" in frame.columns
    assert "Coverage_Ratio" in frame.columns
    assert "Coverage_Status" in frame.columns
    assert "SQRE Expanded Historical Data Availability Report" in report
    assert "Total Samples: 3" in report
    assert "Available Full: 1" in report
    assert "Available Partial: 1" in report
    assert "Missing: 1" in report
    assert "Partial Samples:" in report
    assert "- H1: total=1, available_full=0, available_partial=0, missing=1, invalid=0" in report


def test_report_contains_no_forbidden_operational_language(tmp_path):
    module = _load_module()
    report_path = module.write_availability_report(
        tmp_path / "availability.txt",
        {"sample_set_name": "sample_set"},
        set(),
        [],
    )

    report = report_path.read_text(encoding="utf-8")
    forbidden = [
        "Buy",
        "Sell",
        "Entry",
        "Exit",
        "Trade signal",
        "Trade setup",
        "Take profit",
        "Stop loss",
        "Profitable",
        "Opportunity",
        "Recommendation to trade",
        "Edge",
        "Best timeframe",
        "Best profile",
        "Should trade",
        "Predicts",
    ]
    assert not any(term in report for term in forbidden)


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


def test_cli_accepts_coverage_tolerance_arguments(tmp_path):
    samples_config = tmp_path / "samples.yaml"
    validation_config = tmp_path / "validation.yaml"
    output_csv = tmp_path / "availability.csv"
    output_report = tmp_path / "availability.txt"
    ohlc_path = tmp_path / "EURUSD_M5_period_3.csv"
    _write_ohlc(ohlc_path, ["2026-01-01 00:00:00", "2026-01-02 00:00:00"])
    samples_config.write_text(
        f"""
sample_set_name: sample_set
symbol: EURUSD
provider: twelvedata
pip_size: 0.0001
samples:
  - sample_id: eurusd_m5_period_3
    symbol: EURUSD
    timeframe: M5
    start: 2026-01-01
    end: 2026-01-02
    output_path: {ohlc_path}
""",
        encoding="utf-8",
    )
    validation_config.write_text(
        """
validation_name: sample
scenarios:
  - scenario_id: eurusd_m5_period_3
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/check_expanded_sample_data.py",
            "--samples-config",
            str(samples_config),
            "--validation-config",
            str(validation_config),
            "--output",
            str(output_csv),
            "--report",
            str(output_report),
            "--min-coverage-ratio",
            "0.90",
            "--max-start-gap-days",
            "7",
            "--max-end-gap-days",
            "7",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Available full: 1" in completed.stdout
    assert output_csv.exists()
    assert output_report.exists()


def _sample(
    sample_id: str,
    timeframe: str,
    output_path: Path,
    *,
    start: str = "2026-01-01",
    end: str = "2026-01-02",
) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "symbol": "EURUSD",
        "timeframe": timeframe,
        "start": start,
        "end": end,
        "output_path": str(output_path),
    }


def _write_ohlc(path: Path, dates: list[str]) -> None:
    rows = [
        {
            "Date": value,
            "Open": 1.1,
            "High": 1.2,
            "Low": 1.0,
            "Close": 1.15,
            "Volume": 0,
        }
        for value in dates
    ]
    pd.DataFrame(rows).to_csv(path, index=False)


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
