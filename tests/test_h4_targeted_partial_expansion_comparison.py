from sqre.h4_targeted_partial_expansion_validation.models import (
    BaselineMetrics,
    PartialCandidate,
    PartialPriceOutcomeSummary,
    PartialStructureStateSummary,
    PartialTransitionSummary,
)
from sqre.h4_targeted_partial_expansion_validation.partial_vs_baseline_review import (
    build_partial_vs_baseline_comparison,
    classify_comparison,
)


def test_comparison_ratios_and_classes():
    candidate = PartialCandidate("cid", "EURUSD", "H4", "PARTIAL_SAMPLE", "FEASIBLE_PARTIAL_SAMPLE", 0.6)
    structure = PartialStructureStateSummary("cid", "PARTIAL_SAMPLE", 500, 25, 100, 5, 4, "A", "DIVERSE", "ok")
    transition = PartialTransitionSummary("cid", "PARTIAL_SAMPLE", 20, 5, "A -> B", 1, 1, 1, "ok")
    price = PartialPriceOutcomeSummary("cid", "PARTIAL_SAMPLE", 10, 8, 2, 0, 11.0, 7.0, 0.5, "ok")
    baseline = BaselineMetrics(4, 1000, 50, 50, 40, 10.0, 8.0)

    comparison = build_partial_vs_baseline_comparison(candidate, structure, transition, price, baseline)

    assert comparison.structure_count_vs_baseline_ratio == 0.5
    assert comparison.forward_range_vs_baseline_ratio == 1.1
    assert comparison.partial_comparison_class == "CONSISTENT_WITH_BASELINE_RANGE"


def test_comparison_classification_variants():
    assert classify_comparison(1.4, 1.0) == "ELEVATED_VS_BASELINE"
    assert classify_comparison(0.6, 0.5) == "LOWER_THAN_BASELINE"
    assert classify_comparison(0.6, 1.1) == "INCONCLUSIVE_COMPARISON"
