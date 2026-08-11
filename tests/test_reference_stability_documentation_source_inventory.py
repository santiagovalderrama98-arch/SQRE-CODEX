from __future__ import annotations

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig
from sqre.reference_stability_documentation.source_inventory import build_source_inventory, has_missing_required_inputs
from tests.test_reference_stability_documentation_loader import write_synthetic_documentation_inputs


def test_source_inventory_reports_loaded_and_missing_files(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)

    rows = build_source_inventory(config)

    assert any(row.source_name == "reference_stability_scorecard" and row.load_status == "LOADED" for row in rows)
    assert not has_missing_required_inputs(rows)


def test_source_inventory_flags_missing_required_inputs(tmp_path):
    config = ReferenceStabilityDocumentationConfig(stability_validation_dir=tmp_path / "missing")

    rows = build_source_inventory(config)

    assert has_missing_required_inputs(rows)
    assert any(row.load_status == "REQUIRED_INPUT_MISSING" for row in rows)
