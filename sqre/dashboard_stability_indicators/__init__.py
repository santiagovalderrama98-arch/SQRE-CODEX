"""Dashboard stability indicators for SQRE research dashboards."""

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.dashboard_stability_indicators_pipeline import (
    DashboardStabilityIndicatorsPipeline,
)

__all__ = ["DashboardStabilityIndicatorsConfig", "DashboardStabilityIndicatorsPipeline"]
