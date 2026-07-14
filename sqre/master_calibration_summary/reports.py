"""Report writers for master historical calibration summaries."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.master_calibration_summary.models import MasterCalibrationSummaryResult


def write_master_summary_csv(path: Path | str, frame: pd.DataFrame) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)


def write_master_summary_report(path: Path | str, result: MasterCalibrationSummaryResult) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(result), encoding="utf-8")


def _build_report(result: MasterCalibrationSummaryResult) -> str:
    lines = [
        "SQRE Master Historical Calibration Summary",
        "=========================================",
        "",
        "Generated At",
        "------------",
        datetime.now(timezone.utc).isoformat(),
        "",
        "Input Summary Files",
        "-------------------",
        f"- Total requested: {len(result.requested_files)}",
        f"- Found: {len(result.found_files)}",
        f"- Missing: {len(result.missing_files)}",
    ]
    lines.extend([f"- FOUND: {path}" for path in result.found_files] or ["- FOUND: NONE"])
    lines.extend(["", "Rows Loaded", "-----------", str(result.rows_loaded)])
    lines.extend(["", "Rows Retained", "-------------", str(result.rows_retained)])
    lines.extend(["", "Duplicate Scenario IDs", "----------------------"])
    lines.extend(_duplicate_lines(result))
    lines.extend(["", "Missing Input Files", "-------------------"])
    lines.extend([f"- {path}" for path in result.missing_files] or ["- NONE"])
    lines.extend(["", "Timeframes Covered", "------------------"])
    lines.extend(_timeframe_lines(result))
    lines.extend(["", "Scenario Coverage by Timeframe", "------------------------------"])
    lines.extend(_timeframe_lines(result))
    lines.extend(["", "Retained Scenario IDs", "---------------------"])
    lines.extend(_scenario_id_lines(result))
    lines.extend(
        [
            "",
            "Dedupe Policy",
            "-------------",
            f"- Key: {result.dedupe_key}",
            f"- Policy: {result.dedupe_policy}",
            "",
            "Notes",
            "-----",
            "- This summary is diagnostic and research-only.",
            "- Later summaries are retained when the default policy is last.",
            "- No production defaults were changed.",
            "- No thresholds were changed.",
            "- No operational logic was added.",
            "",
        ]
    )
    return "\n".join(lines)


def _duplicate_lines(result: MasterCalibrationSummaryResult) -> list[str]:
    if not result.duplicate_details:
        return ["- Count: 0", "- IDs: NONE"]

    lines = [f"- Count: {len(result.duplicate_details)}"]
    for detail in result.duplicate_details:
        sources = "; ".join(detail.source_files)
        lines.append(
            f"- {detail.scenario_id}: duplicate_count={detail.duplicate_count}, "
            f"retained_source={detail.retained_source_file}, "
            f"retained_source_row_index={detail.retained_source_row_index}, sources={sources}"
        )
    return lines


def _timeframe_lines(result: MasterCalibrationSummaryResult) -> list[str]:
    if not result.timeframe_counts:
        return ["- NONE"]
    return [f"- {timeframe}: {count}" for timeframe, count in sorted(result.timeframe_counts.items())]


def _scenario_id_lines(result: MasterCalibrationSummaryResult) -> list[str]:
    # Filled by the pipeline through the result's retained frame-derived counts in the report path.
    try:
        frame = pd.read_csv(result.output_path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return ["- NONE"]
    if "Scenario_ID" not in frame.columns or frame.empty:
        return ["- NONE"]
    return [f"- {scenario_id}" for scenario_id in frame["Scenario_ID"].astype(str).tolist()]
