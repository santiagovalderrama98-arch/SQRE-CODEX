from sqre.h4_d1_structural_research.consistency import cv, stability_flag


def test_consistency_cv_calculation_and_zero_mean_are_safe():
    assert round(cv([2, 4, 6]), 4) == 0.4082
    assert cv([0, 0, 0]) == 0.0


def test_forward_range_stability_flag():
    assert stability_flag(0.2, 0.3) == "STABLE"
    assert stability_flag(0.4, 0.3) == "VARIABLE"
