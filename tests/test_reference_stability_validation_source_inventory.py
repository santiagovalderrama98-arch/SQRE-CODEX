from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.source_inventory import build_source_inventory, has_missing_required_inputs
from tests.test_reference_stability_validation_loader import write_synthetic_inputs


def test_source_inventory_reports_loaded_files(tmp_path):
    config = write_synthetic_inputs(tmp_path)

    rows = build_source_inventory(config)

    assert any(row.source_name == "reference_store" and row.load_status == "LOADED" for row in rows)
    assert has_missing_required_inputs(rows) is False


def test_source_inventory_reports_missing_required_files(tmp_path):
    config = ReferenceStabilityValidationConfig(
        reference_store_dir=tmp_path / "missing_reference",
        query_interface_dir=tmp_path / "missing_query",
    )

    rows = build_source_inventory(config)

    assert has_missing_required_inputs(rows) is True
