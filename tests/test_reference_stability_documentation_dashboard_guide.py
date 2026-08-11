from __future__ import annotations

import pandas as pd

from sqre.reference_stability_documentation.dashboard_reading_guide_builder import (
    DASHBOARD_ELEMENTS,
    build_dashboard_reading_guide,
)


def test_dashboard_reading_guide_includes_all_required_elements():
    guide = build_dashboard_reading_guide(True, pd.DataFrame({"Reference_Card_ID": ["CARD_1"]}))

    assert set(guide["Dashboard_Element"]) == set(DASHBOARD_ELEMENTS)
    assert len(guide) == 12
