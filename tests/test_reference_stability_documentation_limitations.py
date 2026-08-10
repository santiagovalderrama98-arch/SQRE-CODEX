from __future__ import annotations

from sqre.reference_stability_documentation.limitation_documentation_builder import (
    LIMITATION_CATEGORIES,
    build_limitations_documentation,
)


def test_limitations_builder_documents_required_limitations():
    limitations = build_limitations_documentation()

    assert set(LIMITATION_CATEGORIES).issubset(set(limitations["Limitation_Category"]))
    assert any("Partial horizon stability" in text for text in limitations["Limitation_Text"])
    assert any("Directional instability" in text for text in limitations["Limitation_Text"])
