from pathlib import Path

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.h4_source_resolver import build_source_inventory, resolve_h4_source


def test_resolve_h4_source_prefers_explicit_existing_input(tmp_path: Path):
    h4_input = tmp_path / "EURUSD_H4.csv"
    pd.DataFrame({"Date": ["2026-07-01"], "Open": [1], "High": [1], "Low": [1], "Close": [1]}).to_csv(
        h4_input, index=False
    )
    config = H4D1SynchronizedDataPreparationConfig(h4_input=h4_input)

    assert resolve_h4_source(config) == h4_input


def test_source_inventory_reports_missing_isolated_inputs(tmp_path: Path):
    config = H4D1SynchronizedDataPreparationConfig(
        h4_input=tmp_path / "missing_h4.csv",
        validation_config=tmp_path / "missing_config.yaml",
        validation_summary=tmp_path / "missing_summary.csv",
    )

    rows = build_source_inventory(config, resolve_h4_source(config))

    assert rows[0].load_status == "MISSING"
    assert rows[1].load_status == "MISSING"
    assert all(row.rows_loaded == 0 for row in rows)


def test_source_inventory_records_optional_download_as_skipped(tmp_path: Path):
    config = H4D1SynchronizedDataPreparationConfig(
        h4_input=tmp_path / "missing_h4.csv",
        allow_download=True,
        provider="twelvedata",
    )

    rows = build_source_inventory(config, resolve_h4_source(config))

    assert rows[-1].source_name == "optional_download"
    assert rows[-1].load_status == "SKIPPED_DOWNLOAD_NOT_IMPLEMENTED"
