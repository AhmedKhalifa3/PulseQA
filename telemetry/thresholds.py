"""
Resource Consumption Threshold & Assertion Engine.
Validates that automated test executions do not exceed hardware consumption budgets.
"""

import logging
from typing import Optional

from core.exceptions import ResourceThresholdExceededError
from telemetry.monitor import TelemetryResult

logger = logging.getLogger("PulseQA.Thresholds")


def assert_resource_limits(
    result: TelemetryResult,
    max_cpu_pct: float | None = None,
    max_avg_cpu_pct: float | None = None,
    max_ram_mb: float | None = None,
    max_ram_growth_mb: float | None = None,
):
    """
    Asserts that measured resource consumption stayed within defined SLAs.
    Raises ResourceThresholdExceededError if any threshold is violated.
    """
    logger.info(
        f"[Resource Validation] '{result.test_name}': "
        f"Peak CPU: {result.peak_cpu_percent:.1f}%, Avg CPU: {result.avg_cpu_percent:.1f}%, "
        f"Peak RAM: {result.peak_memory_rss_mb:.1f}MB, Growth: {result.memory_growth_mb:+.1f}MB"
    )

    if max_cpu_pct is not None and result.peak_cpu_percent > max_cpu_pct:
        raise ResourceThresholdExceededError(
            metric_name="Peak CPU Usage (%)",
            actual_value=result.peak_cpu_percent,
            threshold_value=max_cpu_pct,
            test_name=result.test_name,
        )

    if max_avg_cpu_pct is not None and result.avg_cpu_percent > max_avg_cpu_pct:
        raise ResourceThresholdExceededError(
            metric_name="Average CPU Usage (%)",
            actual_value=result.avg_cpu_percent,
            threshold_value=max_avg_cpu_pct,
            test_name=result.test_name,
        )

    if max_ram_mb is not None and result.peak_memory_rss_mb > max_ram_mb:
        raise ResourceThresholdExceededError(
            metric_name="Peak Memory RSS (MB)",
            actual_value=result.peak_memory_rss_mb,
            threshold_value=max_ram_mb,
            test_name=result.test_name,
        )

    if max_ram_growth_mb is not None and result.memory_growth_mb > max_ram_growth_mb:
        raise ResourceThresholdExceededError(
            metric_name="Memory Growth / Leak (MB)",
            actual_value=result.memory_growth_mb,
            threshold_value=max_ram_growth_mb,
            test_name=result.test_name,
        )
