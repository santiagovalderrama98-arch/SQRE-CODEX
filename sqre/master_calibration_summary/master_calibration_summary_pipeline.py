"""Pipeline for building a master historical calibration summary."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.master_calibration_summary.config import MasterCalibrationSummaryConfig
from sqre.master_calibration_summary.dedupe import dedupe_summary_frame
from sqre.master_calibration_summary.loader import load_summary_csvs
from sqre.master_calibration_summary.models import MasterCalibrationSummaryResult
from sqre.master_calibration_summary.reports import write_master_summary_csv, write_master_summary_report


def build_master_calibration_summary(
    summary_csv_paths: list[Path | str],
    output_path: Path | str,
    report_path: Path | str,
    config: MasterCalibrationSummaryConfig | None = None,
) -> MasterCalibrationSummaryResult:
    active_config = config or MasterCalibrationSummaryConfig()
    loaded = load_summary_csvs(summary_csv_paths, allow_missing_inputs=active_config.allow_missing_inputs)
    deduped = dedupe_summary_frame(
        loaded.frame,
        dedupe_key=active_config.dedupe_key,
        dedupe_policy=active_config.dedupe_policy,
    )

    output = Path(output_path)
    report = Path(report_path)
    write_master_summary_csv(output, deduped.frame)
    result = MasterCalibrationSummaryResult(
        requested_files=loaded.requested_files,
        found_files=loaded.found_files,
        missing_files=loaded.missing_files,
        rows_loaded=deduped.rows_loaded,
        rows_retained=deduped.rows_retained,
        duplicate_scenario_ids=deduped.duplicate_scenario_ids,
        duplicate_details=deduped.duplicate_details,
        timeframe_counts=_timeframe_counts(deduped.frame),
        output_path=output,
        report_path=report,
        dedupe_key=active_config.dedupe_key,
        dedupe_policy=active_config.dedupe_policy,
    )
    write_master_summary_report(report, result)
    return result


def _timeframe_counts(frame: pd.DataFrame) -> dict[str, int]:
    if frame.empty or "Timeframe" not in frame.columns:
        return {}
    counts = frame["Timeframe"].astype(str).value_counts().to_dict()
    return {str(timeframe): int(count) for timeframe, count in counts.items()}
